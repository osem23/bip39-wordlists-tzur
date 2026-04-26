// SPDX-License-Identifier: MIT
// Minimal reference implementation: decode a BIP-39 mnemonic in any supported
// language into its English equivalent and derive the 64-byte seed.
//
// Platform: Apple platforms only (uses CommonCrypto for PBKDF2-HMAC-SHA512).
// Swift 5.9+ is recommended. No external dependencies.
//
// Build:
//   swiftc -O Decode.swift -o decode
//
// Or run in a Swift playground / Xcode. The repository root is resolved
// relative to the source file via #filePath.
//
// Usage:
//   ./decode <language> "<native mnemonic>" [passphrase]
//
// Examples:
//   ./decode arabic "تخلي تخلي ... حول" TREZOR
//   ./decode hebrew "נטוש נטוש ... אודות"
//   ./decode english "abandon abandon ... about"

import Foundation
import CommonCrypto

// MARK: - Paths

let repoRoot: URL = {
    let src = URL(fileURLWithPath: #filePath)
    return src.deletingLastPathComponent()   // examples/swift
              .deletingLastPathComponent()   // examples
              .deletingLastPathComponent()   // repo root
}()

let wordlistsDir = repoRoot.appendingPathComponent("wordlists")

// MARK: - Language catalog

// English is the canonical BIP-39 source; all 30 non-English languages ship
// as TZUR Original display wordlists (index-paired translations of English).
let languageToPath: [String: String] = {
    var map: [String: String] = ["english": "reference-canonical/english.txt"]
    let tzur = [
        "arabic", "bengali", "chinese_simplified", "chinese_traditional", "czech",
        "danish", "dutch", "estonian", "farsi", "filipino", "french", "german",
        "hebrew", "hindi", "indonesian", "italian", "japanese", "korean", "malay",
        "polish", "portuguese", "romanian", "russian", "spanish", "swedish",
        "thai", "turkish", "ukrainian", "urdu", "vietnamese",
    ]
    for lang in tzur {
        map[lang] = "tzur-original/\(lang).txt"
    }
    return map
}()

// MARK: - Wordlist loading

enum DecodeError: Error {
    case unsupportedLanguage(String)
    case unknownWord(String, String)
    case invalidWordlist(String)
    case invalidMnemonicLength(Int)
    case checksumMismatch
}

func loadWordlist(_ language: String) throws -> [String] {
    guard let rel = languageToPath[language] else {
        throw DecodeError.unsupportedLanguage(language)
    }
    let url = wordlistsDir.appendingPathComponent(rel)
    let text = try String(contentsOf: url, encoding: .utf8)
    let words = text.replacingOccurrences(of: "\r", with: "")
                    .trimmingCharacters(in: .whitespacesAndNewlines)
                    .split(separator: "\n")
                    .map(String.init)
    guard words.count == 2048 else {
        throw DecodeError.invalidWordlist(rel)
    }
    return words
}

// MARK: - Mnemonic conversion

func splitMnemonic(_ mnemonic: String) -> [String] {
    // Handles ASCII space and ideographic space (U+3000) used by Japanese.
    mnemonic.trimmingCharacters(in: .whitespacesAndNewlines)
            .split { $0.isWhitespace || $0 == "\u{3000}" }
            .map(String.init)
}

func nativeToEnglish(_ mnemonic: String, language: String) throws -> String {
    if language == "english" {
        return mnemonic.trimmingCharacters(in: .whitespacesAndNewlines)
    }
    let native = try loadWordlist(language)
    let english = try loadWordlist("english")
    var index: [String: Int] = [:]
    index.reserveCapacity(native.count)
    for (i, w) in native.enumerated() { index[w] = i }

    var out: [String] = []
    for word in splitMnemonic(mnemonic) {
        guard let i = index[word] else {
            throw DecodeError.unknownWord(word, language)
        }
        out.append(english[i])
    }
    return out.joined(separator: " ")
}

// MARK: - BIP-39 checksum

func sha256Digest(_ data: Data) -> Data {
    var digest = Data(count: Int(CC_SHA256_DIGEST_LENGTH))
    digest.withUnsafeMutableBytes { dbuf in
        data.withUnsafeBytes { ibuf in
            _ = CC_SHA256(
                ibuf.baseAddress,
                CC_LONG(data.count),
                dbuf.bindMemory(to: UInt8.self).baseAddress
            )
        }
    }
    return digest
}

func validateChecksum(_ englishMnemonic: String) throws {
    // BIP-39 CS = ENT/32 checksum bits at the tail of concatenated 11-bit
    // word indices. CS must equal SHA-256(ENT)[:CS_bits]. A reference decoder
    // must reject any mnemonic whose checksum does not verify; otherwise a
    // single mistyped word silently produces a wrong seed.
    let words = englishMnemonic
        .trimmingCharacters(in: .whitespacesAndNewlines)
        .split { $0.isWhitespace }
        .map(String.init)
    let n = words.count
    guard [12, 15, 18, 21, 24].contains(n) else {
        throw DecodeError.invalidMnemonicLength(n)
    }
    let english = try loadWordlist("english")
    var indexMap: [String: Int] = [:]
    indexMap.reserveCapacity(english.count)
    for (i, w) in english.enumerated() { indexMap[w] = i }
    var indices: [Int] = []
    indices.reserveCapacity(n)
    for w in words {
        guard let i = indexMap[w] else {
            throw DecodeError.unknownWord(w, "english")
        }
        indices.append(i)
    }
    var bits = ""
    bits.reserveCapacity(n * 11)
    for idx in indices {
        let raw = String(idx, radix: 2)
        bits.append(String(repeating: "0", count: 11 - raw.count) + raw)
    }
    let entLen = (n * 32) / 3   // 128, 160, 192, 224, 256
    let csLen = entLen / 32     // 4, 5, 6, 7, 8
    let entBits = String(bits.prefix(entLen))
    let csBits = String(bits.suffix(csLen))
    var entBytes = Data(capacity: entLen / 8)
    var i = 0
    while i < entLen {
        let start = entBits.index(entBits.startIndex, offsetBy: i)
        let end = entBits.index(start, offsetBy: 8)
        guard let byte = UInt8(String(entBits[start..<end]), radix: 2) else {
            throw DecodeError.checksumMismatch
        }
        entBytes.append(byte)
        i += 8
    }
    let digest = sha256Digest(entBytes)
    var digestBits = ""
    digestBits.reserveCapacity(digest.count * 8)
    for b in digest {
        let raw = String(b, radix: 2)
        digestBits.append(String(repeating: "0", count: 8 - raw.count) + raw)
    }
    let expected = String(digestBits.prefix(csLen))
    if csBits != expected {
        throw DecodeError.checksumMismatch
    }
}

// MARK: - PBKDF2-HMAC-SHA512

func pbkdf2SHA512(password: Data, salt: Data, iterations: Int, keyLength: Int) -> Data {
    var derived = Data(count: keyLength)
    derived.withUnsafeMutableBytes { derivedBuf in
        password.withUnsafeBytes { passwordBuf in
            salt.withUnsafeBytes { saltBuf in
                _ = CCKeyDerivationPBKDF(
                    CCPBKDFAlgorithm(kCCPBKDF2),
                    passwordBuf.bindMemory(to: Int8.self).baseAddress, password.count,
                    saltBuf.bindMemory(to: UInt8.self).baseAddress, salt.count,
                    CCPseudoRandomAlgorithm(kCCPRFHmacAlgSHA512),
                    UInt32(iterations),
                    derivedBuf.bindMemory(to: UInt8.self).baseAddress, keyLength
                )
            }
        }
    }
    return derived
}

func mnemonicToSeed(_ mnemonic: String, passphrase: String = "") -> Data {
    // BIP-39: NFKD both inputs before PBKDF2.
    let m = mnemonic.decomposedStringWithCompatibilityMapping
    let s = ("mnemonic" + passphrase).decomposedStringWithCompatibilityMapping
    return pbkdf2SHA512(
        password: Data(m.utf8),
        salt:     Data(s.utf8),
        iterations: 2048,
        keyLength:  64
    )
}

// MARK: - CLI

func hexString(_ data: Data) -> String {
    data.map { String(format: "%02x", $0) }.joined()
}

let args = CommandLine.arguments
guard args.count >= 3 else {
    FileHandle.standardError.write(Data(
        "usage: decode <language> \"<native mnemonic>\" [passphrase]\n".utf8
    ))
    exit(1)
}

do {
    let language = args[1].lowercased()
    let mnemonic = args[2]
    let passphrase = args.count >= 4 ? args[3] : ""

    let english = try nativeToEnglish(mnemonic, language: language)
    // Verify the BIP-39 checksum on the canonical English form. Catches
    // transcription errors before they propagate into the derived seed.
    try validateChecksum(english)
    // Display-layer convention: PBKDF2 runs on the canonical English mnemonic,
    // not on the native-language display form. See docs/BIP-multilingual-mnemonics.md.
    let seed = mnemonicToSeed(english, passphrase: passphrase)

    let obj: [String: Any] = [
        "language":          language,
        "mnemonic_input":    mnemonic,
        "mnemonic_english":  english,
        "passphrase":        passphrase,
        "seed":              hexString(seed),
    ]
    let json = try JSONSerialization.data(
        withJSONObject: obj,
        options: [.prettyPrinted, .withoutEscapingSlashes, .sortedKeys]
    )
    FileHandle.standardOutput.write(json)
    FileHandle.standardOutput.write(Data("\n".utf8))
} catch {
    FileHandle.standardError.write(Data("error: \(error)\n".utf8))
    exit(1)
}
