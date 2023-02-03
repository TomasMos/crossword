# Crossword

## This crossword generator was developed as part of my CS50AI course from Harvard. The generator takes two inputs, a structures.txt file which defines the shape of the intended crossword, and a words.txt file which contains a list of available words to be added to the crossword. This is an optimization problem which requires enforcing node consistency, arc consistency and backtracking. 

## Node consistency is implemented by ensuring that the unary constraints are met for each required word. Ie, if the crossword requires a word of 5 letters, then only words of 5 letters in length are left in the domain of possible choices for that particular crossword section. Please refer to example 1 below, the domain for 'infer' would only contain words of 5 letters, and the domain for 'intelligence' would only contain words of 12 letters, and so on. 

#### Example 1.

![Home Page](https://raw.githubusercontent.com/TomasMos/crossword/main/screenshots/structure1_words1.png)

## Arc consistency is achieved by ensuring that neighbouring words share the correct letter where required. Please refer to example 2 below, where 'rural' shares a cell with 'relationship', this is an arc and for there to be consistency, these words must have the same letter for there respective cells. The algorithm does this by choosing a word from the most restrictive domain, which in this case is 'relationship' because of it's length and number of neighbours, and then cycles through the possible options from the domain of the other word 'rural'. When it finds a matching word, it then chooses the next neighbour of 'relationship' and repeats the process. 

#### Output 2.

![Home Page](https://raw.githubusercontent.com/TomasMos/crossword/main/screenshots/structure1_words2.png)

Lastly, backtracking is required when the algorithm cannot match a word from the available words in that domain. For example if there were no words in the domain for the 'carbon' option in example 2 above that satisfied the requirements of being 6 letters and having an 'r' at the third letter. Then, backtracking would be employed by going to the previous word, which in this case is 'confirm' and cycling through the available options that satisfy the required unary and arc constraints for that set of cells. If there are no options that work there, then backtracking would be called again on the word that preceded 'confirm', and so on. 


