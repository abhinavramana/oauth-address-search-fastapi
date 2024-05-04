from models import MatchedZipCode


class TrieNode:
    def __init__(self):
        """
        to represent each node in the trie.
        Each node contains a dictionary of its children nodes, a flag indicating if it's the end of a city name, and a list of associated zip code data.
        """
        self.children = {}
        self.is_end = False
        self.zip_codes = []


def add_to_trie(trie: TrieNode, city, zip_code_data):
    """
    insert city names and their corresponding zip code data into the trie structure.
    """
    node = trie
    for char in city.lower():
        if char not in node.children:
            node.children[char] = TrieNode()
        node = node.children[char]
    node.is_end = True
    node.zip_codes.append(zip_code_data)


def search_trie(trie: TrieNode, city: str):
    """
    performs a prefix search on the trie based on the input city name. It returns a list of MatchedZipCode instances, where the score represents the length of the matching prefix.
    """
    node = trie
    for char in city.lower():
        if char not in node.children:
            return []
        node = node.children[char]

    def dfs(node, score):
        results = []
        if node.is_end:
            for zip_code_data in node.zip_codes:
                results.append(MatchedZipCode(score=score, **zip_code_data.dict()))
        for char in node.children:
            results.extend(dfs(node.children[char], score + 1))
        return results

    return dfs(node, 0)