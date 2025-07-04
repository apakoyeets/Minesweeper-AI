import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game.
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        If the number of cells equals the count (and count > 0),
        then every cell in the set must be a mine.
        """
        if len(self.cells) == self.count and self.count > 0:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        If the count is 0 then every cell in self.cells is safe.
        """
        if self.count == 0:
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        Removes the cell from self.cells and decrements count by 1.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        Simply removes the cell from self.cells.
        """
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player.
    Keeps track of moves made, cells known to be safe or mines,
    and a knowledge base of logical sentences about the game.
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        1) Mark the cell as a move that has been made.
        2) Mark the cell as safe.
        3) Add a new sentence to the AI's knowledge base based on the value
           of `cell` and `count`.
        4) Mark any additional cells as safe or as mines if it can be concluded
           based on the AI's knowledge base.
        5) Add any new sentences to the AI's knowledge base if they can be inferred
           from existing knowledge.
        """
        # 1) Mark move and safe
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # 2) Determine the set of neighboring cells
        neighbors = set()
        i, j = cell
        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                # Skip the cell itself
                if di == 0 and dj == 0:
                    continue
                new_cell = (i + di, j + dj)
                if 0 <= new_cell[0] < self.height and 0 <= new_cell[1] < self.width:
                    neighbors.add(new_cell)

        # 3) Remove from neighbors all cells already known to be safe or mines,
        # and adjust count for any neighboring mines that are already known.
        neighbors = neighbors - self.safes - self.mines
        count -= sum(1 for neighbor in neighbors if neighbor in self.mines)

        # 4) Add the new sentence to the knowledge base, if nonempty.
        if neighbors:
            self.knowledge.append(Sentence(neighbors, count))

        # 5) Update knowledge base with new information.
        self.update_knowledge()

    def update_knowledge(self):
        """
        Continuously update the knowledge base:
          - Mark cells as safe or as mines if their status can be conclusively determined.
          - Infer new sentences from existing sentences if one sentence is a subset of another.
        """
        something_changed = True
        while something_changed:
            something_changed = False
            new_safes = set()
            new_mines = set()

            # Identify all new safe cells and mines from the existing knowledge.
            for sentence in self.knowledge:
                new_safes |= sentence.known_safes()
                new_mines |= sentence.known_mines()

            # Mark any new safe cells.
            for cell in new_safes:
                if cell not in self.safes:
                    self.mark_safe(cell)
                    something_changed = True

            # Mark any new mines.
            for cell in new_mines:
                if cell not in self.mines:
                    self.mark_mine(cell)
                    something_changed = True

            # Remove any empty sentences.
            self.knowledge = [s for s in self.knowledge if s.cells]

            # Infer new sentences from existing knowledge.
            new_sentences = []
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 == sentence2:
                        continue
                    if sentence2.cells.issubset(sentence1.cells):
                        new_cells = sentence1.cells - sentence2.cells
                        new_count = sentence1.count - sentence2.count
                        new_sentence = Sentence(new_cells, new_count)
                        if new_sentence not in self.knowledge and new_sentence not in new_sentences:
                            if new_sentence.cells:
                                new_sentences.append(new_sentence)
            if new_sentences:
                self.knowledge.extend(new_sentences)
                something_changed = True

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe and not already made.
        """
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Chooses randomly among cells that have not been chosen and are not known to be mines.
        """
        choices = []
        for i in range(self.height):
            for j in range(self.width):
                cell = (i, j)
                if cell not in self.moves_made and cell not in self.mines:
                    choices.append(cell)
        if choices:
            return random.choice(choices)
        return None
