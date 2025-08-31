//
//  TokenizerUtils.swift
//  DigitalGuardianSimple
//
//  Simple tokenization utilities for OpenELM Core ML integration
//

import Foundation
import CoreML

class TokenizerUtils {
    // Enhanced tokenization with bidirectional mapping for text generation
    static let vocabulary: [String: Int32] = [
        "<pad>": 0, "<start>": 1, "what": 2, "is": 3, "the": 4, "phone": 5, "number": 6, "for": 7,
        "call": 8, "contact": 9, "help": 10, "service": 11, "government": 12,
        "ato": 13, "medicare": 14, "centrelink": 15, "hospital": 16,
        "emergency": 17, "tax": 18, "health": 19, "benefits": 20,
        "travel": 21, "advice": 22, "passport": 23, "visa": 24, "smartraveller": 25,
        "australian": 26, "department": 27, "foreign": 28, "affairs": 29, "trade": 30,
        "information": 31, "assistance": 32, "overseas": 33, "consular": 34, "embassy": 35,
        "you": 36, "can": 37, "find": 38, "at": 39, "on": 40, "with": 41, "from": 42,
        "available": 43, "hours": 44, "monday": 45, "friday": 46, "website": 47, "email": 48,
        "verified": 49, "official": 50, "provides": 51, "services": 52, "govt": 53,
        "i": 54, "need": 55, "want": 56, "looking": 57, "where": 58, "how": 59, "when": 60,
        "digital": 61, "guardian": 62, "safe": 63, "legitimate": 64, "scam": 65,
        "agency": 66, "office": 67, "line": 68, "hotline": 69, "support": 70,
        "and": 71, "or": 72, "to": 73, "a": 74, "an": 75, "of": 76, "in": 77, "by": 78,
        ".": 79, ",": 80, "?": 81, "!": 82, ":": 83, ";": 84, "-": 85, "(": 86, ")": 87,
        "13": 88, "1800": 89, "02": 90, "03": 91, "07": 92, "08": 93, "131": 94, "132": 95,
        "<unk>": 100, "<end>": 101
    ]
    
    static let reverseVocabulary: [Int32: String] = {
        return Dictionary(uniqueKeysWithValues: vocabulary.map { ($1, $0) })
    }()
    
    static func tokenize(_ text: String) -> [Int32] {
        // Enhanced tokenization for better LLM input
        let preprocessed = text.lowercased()
            .replacingOccurrences(of: "?", with: " ? ")
            .replacingOccurrences(of: ".", with: " . ")
            .replacingOccurrences(of: ",", with: " , ")
        
        let words = preprocessed.components(separatedBy: CharacterSet.whitespacesAndNewlines)
            .filter { !$0.isEmpty }
        
        var tokens: [Int32] = [1] // Start token
        
        for word in words {
            if let tokenId = vocabulary[word] {
                tokens.append(tokenId)
            } else {
                tokens.append(100) // Unknown token
            }
        }
        
        // Pad or truncate to exactly 128 tokens (model requirement)
        while tokens.count < 128 {
            tokens.append(0) // Padding token
        }
        if tokens.count > 128 {
            tokens = Array(tokens.prefix(128))
        }
        
        return tokens
    }
    
    static func detokenize(_ tokens: [Int32]) -> String {
        let words = tokens.compactMap { tokenId -> String? in
            if tokenId == 0 { return nil } // Skip padding
            return reverseVocabulary[tokenId] ?? "<unk>"
        }
        
        return words.joined(separator: " ")
            .replacingOccurrences(of: " ? ", with: "? ")
            .replacingOccurrences(of: " . ", with: ". ")
            .replacingOccurrences(of: " , ", with: ", ")
            .trimmingCharacters(in: .whitespaces)
    }
    
    static func generateNextToken(from logits: MLMultiArray) -> Int32 {
        // Find the token with highest probability (greedy decoding)
        var maxValue: Float = -Float.infinity
        var maxIndex: Int32 = 0
        
        let count = logits.shape[logits.shape.count - 1].intValue // Last dimension is vocab size
        
        for i in 0..<count {
            let value = logits[[0, 127, i] as [NSNumber]].floatValue // Last token position
            if value > maxValue {
                maxValue = value
                maxIndex = Int32(i)
            }
        }
        
        return maxIndex
    }
}
