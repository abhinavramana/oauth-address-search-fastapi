class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end_of_word = False
        self.zip_codes = []


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word, zip_code):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.zip_codes.append(zip_code)

    def search(self, word: str, max_results: int):
        node = self.root
        for char in word.lower():
            if char in node.children:
                node = node.children[char]
            else:
                return []

        # Find all words under this prefix
        results = []
        self._dfs(node, word, results)
        results = sorted(results, key=lambda x: (-x[1], x[0]))[:max_results]
        return results

    def _dfs(self, node, prefix, results):
        if node.is_end_of_word:
            for zip_code in node.zip_codes:
                # Simulate a score based on how exact the match is, for now just using length of prefix
                results.append((zip_code, len(prefix)))
        for char, child in node.children.items():
            self._dfs(child, prefix + char, results)
