from audioop import cross
from ctypes import sizeof
from queue import Empty
import sys
import copy
from crossword import *
import math


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # loop through all variables
        for variable in self.crossword.variables:
            for word in copy.copy(self.domains[variable]):
                if len(word) != variable.length:
                    self.domains[variable].remove(word)


    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revision = 0 
        ol = self.crossword.overlaps[x, y]

        for wordx in copy.copy(self.domains[x]):
            count = 0
            for wordy in self.domains[y]:
                if wordx[ol[0]] == wordy[ol[1]]:
                    count += 1

            if count == 0: 
                self.domains[x].remove(wordx)
                revision += 1
        

        if revision > 0:
            return True
        
        return False
        

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # check if arcs is None, if none, make a queue of arcs (arcs are a list of tuples where a tuple (x, y) is of two neighbouring variables)
        queue = set()

        if arcs is None:
            for variablex in self.crossword.variables:
                for variabley in self.crossword.variables:
                    if variabley != variablex:
                        if self.crossword.overlaps[variablex, variabley] != None:
                            queue.add((variablex, variabley))
        # if arcs is not None, use arcs
        else: 
            queue = arcs

        
        while len(queue) > 0:
            # (x,y) = Dequeue(queue)
            item = queue.pop()

            # check if the relationship needed to be revised
            if self.revise(item[0], item[1]):
                # check if the x domain is not empty
                if self.domains[item[0]] == 0:
                    return False

                # for each Z in X.neighbors - {Y}:
                # Enqueue(queue, (Z,X))
                for z in self.crossword.neighbors(item[0]):
                    if z != item[1]:
                        queue.add((z, item[0]))        
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for val in assignment.values():
            # print(val)
            if val == '':
                return False

        return True 

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # check if each value is distinct        
        for val1 in assignment.values():
            count = 0 
            for val2 in assignment.values():
                if val1 == val2 and val1 != '':
                    count += 1
                if count == 2: 
                    return False
        
        # find the current variable that is under inspection
        tmp = 0
        for variable in assignment:  
            if assignment[variable] == '':
                break
            tmp = variable
        
        
        # Check if current variable value is of the correct length
        if tmp.length != len(assignment[tmp]):
            return False
        
        
        # loop through neighbors and check for consistency
        for neigh in self.crossword.neighbors(tmp):
            # print(f"naighbor is {assignment[neigh]}")
            ol = self.crossword.overlaps[tmp, neigh]
            # print(ol)
            if assignment[neigh] == '':
                continue
            if assignment[tmp][ol[0]] != assignment[neigh][ol[1]]:
                return False
        # if all checks are passed, give green light 
        return True
        

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # temporary return value... will make more sophisticated later
        
        return list(self.domains[var])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Vcount = math.inf
        # # loop through assignment 
        # for variable in assignment:
        #     # find variables with no assignment
        #     if assignment[variable] == '':
        #         length = len(self.domains[variable])
        #         # find the variable with the fewest number of words in its domain 
        #         if length < Vcount:
        #             V = variable
        #             Vcount = len(self.domains[variable])
        # return V  
 
        
        
        # placeholder function, no sorting    
        for pair in assignment:
            if assignment[pair] == '':
                return pair

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # create assignment structure only the first time backtrack is called
        if len(assignment) == 0:
            for variable in self.crossword.variables:
                assignment[variable] = self.domains[variable].pop() if len(self.domains[variable]) == 1 else ''
                
        # provide an out for the iteration if the assignment is complete
        if self.assignment_complete(assignment):
            return assignment

        # get an unassigned variable from assigment 
        var = self.select_unassigned_variable(assignment)
        #loop through available values for the unassigned variable
        for value in self.domains[var]:
            #create a copy of the current assigment
            assignmentC = copy.copy(assignment)
            # assign the value to the unassigned variable 
            assignmentC[var] = value
            
            #check if the assignment is consistent
            if self.consistent(assignmentC):
                # assign the consistent value to the source of truth for for the assignment 
                assignment[var] = value
                result = self.backtrack(assignment)
                if result != None:
                    return result
                assignment[var] = ''
        return None
            
        


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()
    # print(assignment)
    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
