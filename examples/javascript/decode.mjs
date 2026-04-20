/**
 * Minimal reference implementation: decode a BIP-39 mnemonic in any supported
 * language into its English equivalent and derive the 64-byte seed.
 *
 * Dependencies: Node.js 18+ standard library only (node:crypto, node:fs).
 *
 * Usage:
 *   node decode.mjs <language> "<native mnemonic>" [passphrase]
 *
 * Examples:
 *   node decode.mjs arabic "تخلي تخلي ... حول" TREZOR
 *   node decode.mjs hebrew "נטוש נטוש ... אודות"
 *   node decode.mjs english "abandon abandon ... about"
 */

import { pbkdf2Sync } from "node:crypto";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO_ROOT = resolve(HERE, "..", "..");
const WORDLISTS = resolve(REPO_ROOT, "wordlists");

const LANG_TO_PATH = {
  english:              "official-bip39/english.txt",
  chinese_simplified:   "official-bip39/chinese_simplified.txt",
  chinese_traditional:  "official-bip39/chinese_traditional.txt",
  czech:                "official-bip39/czech.txt",
  french:               "official-bip39/french.txt",
  italian:              "official-bip39/italian.txt",
  japanese:             "official-bip39/japanese.txt",
  korean:               "official-bip39/korean.txt",
  portuguese:           "official-bip39/portuguese.txt",
  spanish:              "official-bip39/spanish.txt",
  hindi:                "community/hindi.txt",
};
for (const tzur of [
  "arabic", "bengali", "danish", "dutch", "estonian", "farsi", "filipino",
  "german", "hebrew", "indonesian", "malay", "polish", "romanian", "russian",
  "swedish", "thai", "turkish", "ukrainian", "urdu", "vietnamese",
]) {
  LANG_TO_PATH[tzur] = `tzur-original/${tzur}.txt`;
}

function loadWordlist(language) {
  const rel = LANG_TO_PATH[language];
  if (!rel) throw new Error(`unsupported language: ${language}`);
  const text = readFileSync(resolve(WORDLISTS, rel), "utf8");
  return text.replace(/\r/g, "").trim().split("\n");
}

function splitMnemonic(mnemonic) {
  // Handles ASCII space and ideographic space (U+3000) used by Japanese.
  return mnemonic.trim().split(/[\s\u3000]+/u);
}

function nativeToEnglish(mnemonic, language) {
  if (language === "english") return mnemonic.trim();

  const native = loadWordlist(language);
  const english = loadWordlist("english");
  const nativeIndex = new Map(native.map((w, i) => [w, i]));

  return splitMnemonic(mnemonic).map(w => {
    const idx = nativeIndex.get(w);
    if (idx === undefined) throw new Error(`word not in ${language} wordlist: ${w}`);
    return english[idx];
  }).join(" ");
}

function mnemonicToSeed(mnemonic, passphrase = "") {
  // BIP-39: NFKD both inputs before PBKDF2.
  const m = mnemonic.normalize("NFKD");
  const s = ("mnemonic" + passphrase).normalize("NFKD");
  return pbkdf2Sync(Buffer.from(m, "utf8"), Buffer.from(s, "utf8"), 2048, 64, "sha512");
}

function main() {
  const [, , langArg, mnemonicArg, passArg] = process.argv;
  if (!langArg || !mnemonicArg) {
    console.error("usage: node decode.mjs <language> \"<native mnemonic>\" [passphrase]");
    process.exit(1);
  }

  const language = langArg.toLowerCase();
  const passphrase = passArg ?? "";
  const english = nativeToEnglish(mnemonicArg, language);
  const seed = mnemonicToSeed(mnemonicArg, passphrase).toString("hex");

  console.log(JSON.stringify({
    language,
    mnemonic_input: mnemonicArg,
    mnemonic_english: english,
    passphrase,
    seed,
  }, null, 2));
}

main();
