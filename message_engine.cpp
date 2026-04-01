#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <map>
#include <unordered_map>
#include <algorithm>
#include <sstream>
#include <cmath>
#include <random>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

class MessageAnalyzer {
private:
    std::map<std::string, std::map<std::string, int>> markovChain;
    std::vector<std::string> vocabulary;
    std::map<std::string, int> wordFreq;
    std::mt19937 rng{std::random_device{}()};

    std::vector<std::string> tokenize(const std::string& text) {
        std::vector<std::string> tokens;
        std::istringstream stream(text);
        std::string word;
        while (stream >> word) {
            // Convert to lowercase
            std::transform(word.begin(), word.end(), word.begin(), ::tolower);
            tokens.push_back(word);
        }
        return tokens;
    }

public:
    void trainFromMessages(const std::vector<std::string>& messages) {
        for (const auto& msg : messages) {
            auto tokens = tokenize(msg);
            
            // Build frequency map
            for (const auto& token : tokens) {
                wordFreq[token]++;
            }

            // Build Markov chain (word -> next word)
            for (size_t i = 0; i < tokens.size() - 1; i++) {
                markovChain[tokens[i]][tokens[i + 1]]++;
            }
        }

        // Extract vocabulary
        for (const auto& pair : wordFreq) {
            vocabulary.push_back(pair.first);
        }
    }

    std::string generateReply(int maxLength = 50) {
        if (vocabulary.empty() || markovChain.empty()) {
            return "hey";
        }

        std::string result;
        std::uniform_int_distribution<> dist(0, vocabulary.size() - 1);

        // Start with a random word
        std::string currentWord = vocabulary[dist(rng)];
        result += currentWord;

        for (int i = 0; i < maxLength; i++) {
            if (markovChain.find(currentWord) == markovChain.end()) {
                break;
            }

            auto& nextWords = markovChain[currentWord];
            int totalCount = 0;
            for (const auto& p : nextWords) {
                totalCount += p.second;
            }

            std::uniform_int_distribution<> wordDist(0, totalCount - 1);
            int random = wordDist(rng);
            int accumulated = 0;

            for (const auto& p : nextWords) {
                accumulated += p.second;
                if (random <= accumulated) {
                    currentWord = p.first;
                    result += " " + currentWord;
                    break;
                }
            }
        }

        return result;
    }

    double calculateConfidence(const std::string& generatedMsg, 
                               const std::vector<std::string>& trainingMsgs) {
        auto tokens = tokenize(generatedMsg);
        int matchCount = 0;

        for (const auto& token : tokens) {
            if (wordFreq.find(token) != wordFreq.end()) {
                matchCount++;
            }
        }

        if (tokens.empty()) return 0.0;
        return static_cast<double>(matchCount) / tokens.size();
    }

    void saveModel(const std::string& filename) {
        json modelData;
        modelData["vocabulary"] = vocabulary;
        modelData["wordFreq"] = wordFreq;
        
        json chainData;
        for (const auto& [word, nexts] : markovChain) {
            json nextWordsJson;
            for (const auto& [nextWord, count] : nexts) {
                nextWordsJson[nextWord] = count;
            }
            chainData[word] = nextWordsJson;
        }
        modelData["markovChain"] = chainData;

        std::ofstream file(filename);
        file << modelData.dump(4);
        file.close();
    }

    void loadModel(const std::string& filename) {
        std::ifstream file(filename);
        if (!file.is_open()) return;

        json modelData;
        file >> modelData;
        file.close();

        vocabulary = modelData["vocabulary"].get<std::vector<std::string>>();
        wordFreq = modelData["wordFreq"].get<std::map<std::string, int>>();

        for (const auto& [word, nexts] : modelData["markovChain"].items()) {
            for (const auto& [nextWord, count] : nexts.items()) {
                markovChain[word][nextWord] = count.get<int>();
            }
        }
    }
};

int main() {
    MessageAnalyzer analyzer;

    // Sample training data (your texting style)
    std::vector<std::string> trainingMessages = {
        "yo whats up man",
        "im down for that",
        "nah not really feeling it",
        "bruhhh that's hilarious",
        "fr fr no cap",
        "lets goooo",
        "idk man seems sus",
        "yeah okay cool",
        "lmaooo stop",
        "literally can't even",
        "ok bet ill be there",
        "nope not happening",
        "thats lowkey fire",
        "my bad i was sleeping",
        "for real though"
    };

    analyzer.trainFromMessages(trainingMessages);
    analyzer.saveModel("message_model.json");

    // Generate sample replies
    std::cout << "=== Generated Replies ===" << std::endl;
    for (int i = 0; i < 5; i++) {
        std::string reply = analyzer.generateReply(15);
        double confidence = analyzer.calculateConfidence(reply, trainingMessages);
        std::cout << "Reply " << i + 1 << ": " << reply 
                  << " [Confidence: " << (confidence * 100) << "%]" << std::endl;
    }

    return 0;
}
