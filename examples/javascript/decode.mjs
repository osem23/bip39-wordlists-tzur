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

// English is the canonical BIP-39 source; all 30 non-English languages ship
// as TZUR Original display wordlists (index-paired translations of English).
const LANG_TO_PATH = { english: "reference-canonical/english.txt" };
for (const tzur of [
  "arabic", "bengali", "chinese_simplified", "chinese_traditional", "czech",
  "danish", "dutch", "estonian", "farsi", "filipino", "french", "german",
  "hebrew", "hindi", "indonesian", "italian", "japanese", "korean", "malay",
  "polish", "portuguese", "romanian", "russian", "spanish", "swedish",
  "thai", "turkish", "ukrainian", "urdu", "vietnamese",
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
  // Display-layer convention: PBKDF2 runs on the canonical English mnemonic,
  // not on the native-language display form. See docs/BIP-multilingual-mnemonics.md.
  const seed = mnemonicToSeed(english, passphrase).toString("hex");

  console.log(JSON.stringify({
    language,
    mnemonic_input: mnemonicArg,
    mnemonic_english: english,
    passphrase,
    seed,
  }, null, 2));
}

main();
