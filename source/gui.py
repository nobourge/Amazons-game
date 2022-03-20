import copy
import time
import datetime
# PyQt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from matrix import Matrix
import amazons
from amazons import *
from pos2d import Pos2D
import guiAI

GRID_DEBUG = False
ACCES_1 = 4
ACCES_2 = 5


def rowcol_to_str(row, col):
    return str(chr(col + 97) + str(row + 1))


def reset(self, N, pos_black, pos_white, pos_arrows):
    self.N = N
    # self.letters = ' '.join(map(chr, range(ord('a'),
    # ord('a')+self.N)))
    self.grid = Matrix(self.N, EMPTY)
    self.history = []
    for positions, value in zip([pos_white, pos_black, pos_arrows],
                                [PLAYER_1, PLAYER_2, ARROW]):
        for pos in positions:
            self.grid[pos] = value
    self.queens = [list(map(Pos2D.from_string, positions))
                   for positions in (pos_white, pos_black)]
    self.nb_arrows = len(pos_arrows)


class App(QMainWindow):
    """
    Main Graphical User Interface class.
    :attribute current_player: Player who should act on the board right now
    :attribute waiting_player: The other player
    :attribute time_interval: integer giving the delay before an AI action
    """
    TITLE = 'Amazon\'s game'

    def __init__(self):
        """
        Constructor of class `App`.
        """
        super().__init__()
        self.init_vars()
        self.current_player = None
        self.waiting_player = None
        self.initUI()

    def initUI(self):
        """
        Instantiation of the interface per se: create all the widgets and
        layouts, and associate them altogether.
        :return: None
        """
        self.desktop = QApplication.desktop()
        self.screenRect = self.desktop.screenGeometry()
        self.height = self.screenRect.height()
        self.width = self.screenRect.width()

        self.setWindowTitle(App.TITLE)
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.main_hbox = QHBoxLayout()
        # self.setAttribute(Qt.WA_TranslucentBackground, True)
        # self.setStyleSheet("background-color:black")
        main_hbox_color_effect = QGraphicsColorizeEffect()
        main_hbox_color_effect.setColor(Qt.black)
        # self.setGraphicsEffect(main_hbox_color_effect)

        self.settings_groupbox = QGroupBox('Settings')
        settings_color_effect = QGraphicsColorizeEffect()
        settings_color_effect.setColor(Qt.white)
        self.settings_grid = QGridLayout()

        self.settings_groupbox.setLayout(self.settings_grid)
        self.settings_groupbox.setFixedSize(QSize(self.width / 4,
                                                  9 * self.height / 10))
        self.players_groupbox = QGroupBox('Players')
        settings_color_effect = QGraphicsColorizeEffect()
        settings_color_effect.setColor(Qt.white)
        self.players_grid = QGridLayout()

        self.players_groupbox.setLayout(self.players_grid)

        player1label = QLabel('Player 1:')
        player1label_color_effect = QGraphicsColorizeEffect()

        player1label_color_effect.setColor(Qt.green)
        player1label.setGraphicsEffect(player1label_color_effect)
        self.players_grid.addWidget(player1label)
        self.cb_player1 = QComboBox()
        self.cb_player1.addItems(['Tournament AI',
                                  'Minimax AI',
                                  'GUI AI',
                                  'Human'])
        self.players_grid.addWidget(self.cb_player1)

        self.add_player_1button = QPushButton('Add queen', self)
        self.players_grid.addWidget(self.add_player_1button)

        player2label = QLabel('Player 2:')
        player2label_color_effect = QGraphicsColorizeEffect()

        player2label_color_effect.setColor(Qt.red)
        player2label.setGraphicsEffect(player2label_color_effect)
        self.players_grid.addWidget(player2label)
        self.cb_player2 = QComboBox()
        self.cb_player2.addItems(['Tournament AI',
                                  'Minimax AI',
                                  'GUI AI',
                                  'Human'])

        self.players_grid.addWidget(self.cb_player2)

        self.add_player_2button = QPushButton('Add queen', self)
        self.players_grid.addWidget(self.add_player_2button)

        self.settings_grid.addWidget(self.players_groupbox)

        self.board_options_groupbox = QGroupBox('Board Options')
        settings_color_effect = QGraphicsColorizeEffect()
        settings_color_effect.setColor(Qt.white)
        self.board_options_grid = QGridLayout()

        self.board_options_groupbox.setLayout(self.board_options_grid)

        self.add_arrow_button = QPushButton('Add arrow', self)
        self.board_options_grid.addWidget(self.add_arrow_button)

        self.load_board_button = QPushButton('Load board', self)
        self.board_options_grid.addWidget(self.load_board_button)

        label = QLabel('Board size:')
        self.board_options_grid.addWidget(label)
        self.board_size_textbox = QLineEdit(self)
        self.board_options_grid.addWidget(self.board_size_textbox)

        self.apply_board_sizebutton = QPushButton('Apply board size')
        # self.apply_board_sizebutton = QPushButton('Apply board size',
        #                                         self)
        self.board_options_grid.addWidget(self.apply_board_sizebutton)
        self.apply_board_sizebutton.clicked.connect(
            self.apply_board_size)

        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset)
        self.board_options_grid.addWidget(self.reset_button)

        self.settings_grid.addWidget(self.board_options_groupbox)

        interval_timer_label = QLabel('Timer interval:')
        timer_label_color_effect = QGraphicsColorizeEffect()
        timer_label_color_effect.setColor(Qt.white)
        interval_timer_label.setGraphicsEffect(timer_label_color_effect)
        self.settings_grid.addWidget(interval_timer_label)
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setTickPosition(QSlider.TicksBelow)
        self.time_slider.sliderReleased.connect(self.release_slider)
        self.time_slider.setTickInterval(10)
        self.time_slider.setValue(1)
        self.settings_grid.addWidget(self.time_slider)

        self.timer_display_label = QLabel('Play Time')
        timer_display_label_color_effect = QGraphicsColorizeEffect()
        #timer_display_label_color_effect.setColor(Qt.white)
        #self.timer_display_label.setGraphicsEffect(
        # timer_label_color_effect)
        self.settings_grid.addWidget(self.timer_display_label)

        self.cb_timer = QComboBox()
        self.cb_timer.addItems(['Timer', 'No Timer'])
        self.settings_grid.addWidget(self.cb_timer)

        self.pause_play_button = QPushButton('Pause', self)
        self.settings_grid.addWidget(self.pause_play_button)
        self.pause_play_button.clicked.connect(
            self.pause_play)

        self.record_button = QPushButton('Record')
        self.record_button.clicked.connect(self.record_game)
        self.settings_grid.addWidget(self.record_button)

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_game)
        self.settings_grid.addWidget(self.start_button)

        self.recorded_games_button = QPushButton('Recorded games')
        self.recorded_games_button.clicked.connect(
            self.exhibit_recorded_games)
        self.settings_grid.addWidget(self.recorded_games_button)

        self.quit_button = QPushButton('Quit')
        self.quit_button.clicked.connect(QCoreApplication.quit)
        self.settings_grid.addWidget(self.quit_button)

        self.main_hbox.addWidget(self.settings_groupbox,
                                 alignment=Qt.AlignLeft)

        self.hbox = QHBoxLayout()

        self.canvas = Canvas(self.board, self.N, self.width,
                             self.height,
                             parent=self.central_widget)

        self.canvas.mousePressEvent = self.handle_click_event

        self.hbox.addWidget(self.canvas, alignment=Qt.AlignCenter)

        self.load_board_button.clicked.connect(
            self.load_board)
        self.add_player_1button.clicked.connect(
            self.add_player_1)
        self.add_player_2button.clicked.connect(
            self.add_player_2)
        self.add_arrow_button.clicked.connect(
            self.add_arrow)

        self.main_hbox.addLayout(self.hbox)

        self.central_widget.setLayout(self.main_hbox)
        self.showMaximized()

    def load_board(self):
        """
        loads a board
        """
        if self.current_player is not None:
            return
        self.N, self.pos_black, self.pos_white, self.pos_arrows = \
            amazons.read_file(
                'plateau.txt')
        self.reset()

    def cancel_active_button(self):
        self.add_player_1button.setText('Add queen')
        self.add_player_2button.setText('Add queen')
        self.add_arrow_button.setText('Add arrow')

    def add_player_1(self):
        self.cancel_active_button()
        self.add_player_1button.setText('Adding queen')
        self.active_button = "adding_player_1"

    def add_player_2(self):
        self.cancel_active_button()
        self.add_player_2button.setText('Adding queen')
        self.active_button = "adding_player_2"

    def add_arrow(self):
        self.cancel_active_button()
        self.add_arrow_button.setText('Adding arrow')
        self.active_button = "adding_arrow"

    def apply_board_size(self):
        """
        sets the board to the user input size
        """
        self.cancel_active_button()
        textboxValue = self.board_size_textbox.text()
        if self.current_player is not None or textboxValue == "":
            return

        self.N = int(textboxValue)
        for p in self.pos_arrows:
            if self.N < int(p[1]):
                self.pos_arrows.remove(p)
        for p in self.pos_white:
            if self.N < int(p[1]):
                self.pos_white.remove(p)
        for p in self.pos_black:
            if self.N < int(p[1]):
                self.pos_black.remove(p)
        self.reset()

        self.board_size_textbox.setText("")

    def release_slider(self):
        """
        Callback of SliderReleased event: update the time interval.
        :return: None
        """
        self.time_interval = self.time_slider.value() * 10

    def pause_play(self):
        if self.pause_play_button.text() == "Pause":
            self.time_interval = INF
            self.pause_play_button.setText("Play")
        else:
            self.release_slider()
            self.pause_play_button.setText("Pause")

    def handle_click_event(self, event):
        """
        Callback of Clicked event on Canvas
        :param event: contains the (x, y) position of the click event
        :return: None
        """
        x = event.x()
        y = event.y()
        row, col = self.canvas.pos2rowcol(x, y)
        if self.N < row or self.N < col:
            return

        if isinstance(self.current_player, HumanPlayer):
            access_show = False
            toggle = False

            if 0 == len(self.action_capacitor):
                if self.board.grid.at(Pos2D(row, col)) == \
                        self.current_player.player_id:
                    self.action_capacitor.append(Pos2D(row, col))
                    self.display_board = copy.deepcopy(self.board)
                    self.display_board.grid.set(Pos2D(row, col),
                                                self.current_player.player_id + 4)
                    access_show = True
                else:
                    return

            elif 0 < len(self.action_capacitor):
                if len(self.action_capacitor) == 1:
                    if self.display_board.at(Pos2D(row,
                                                   col)) == 6:
                        self.action_capacitor.append(Pos2D(row, col))
                        self.unDisplayAccess()
                        self.display_board = copy.deepcopy(self.board)
                        self.display_board.grid.set(
                            self.action_capacitor[-2], EMPTY)
                        self.display_board.grid.set(Pos2D(row, col),
                                                    self.current_player.player_id + 4)
                        access_show = True
                    else:
                        return
                elif len(self.action_capacitor) == 2:
                    if self.display_board.at(Pos2D(row, col)) == 6:
                        self.action_capacitor.append(Pos2D(row, col))
                        self.unDisplayAccess()
                    else:
                        return
            if access_show:
                self.displayAccess()

            if len(self.action_capacitor) == 3:
                try:
                    action = Action(self.action_capacitor[0],
                                    self.action_capacitor[1],
                                    self.action_capacitor[2],
                                    self.current_player.player_id)
                    valid = self.board.is_valid_action(action)
                    if valid:  # todo del
                        self.current_player.play(action)
                        toggle = True
                    self.display_board = self.board
                except InvalidActionError:
                    return
            self.canvas.reset(self.display_board, self.N, self.width,
                              self.height)
            self.canvas.update()
            if toggle:
                self.toggle_players()
        else:
            self.modBoard(row, col)

    def modBoard(self, row, col):
        removed = None
        symbol = self.board.grid.at(Pos2D(row, col))

        if symbol != EMPTY:
            pos = [self.pos_white, self.pos_black, self.pos_arrows]
            pos[symbol].remove(rowcol_to_str(row, col))
            removed = symbol

        if self.active_button == "adding_player_1":
            if removed != PLAYER_1:
                self.pos_white.append(rowcol_to_str(row, col))

        elif self.active_button == "adding_player_2":
            if removed != PLAYER_2:
                self.pos_black.append(rowcol_to_str(row, col))

        elif self.active_button == "adding_arrow":
            if removed != ARROW:
                self.pos_arrows.append(rowcol_to_str(row, col))
        self.reset()

    def possible_moves_from(self, origin, ignore=None):
        """
        Énumère les déplacements possibles depuis une certaine position sur le
         plateau
        Args:
            origin (Pos2D): la position de départ d'une reine
            ignore (Pos2D): une potentielle position à ignorer et None sinon
        """
        for direction in DIRECTIONS:
            new_pos = origin + direction
            while self.display_board.is_valid_pos(new_pos) and (
                    self.display_board.at(new_pos)
                    == EMPTY
                    or (ignore is not None and new_pos == ignore)):
                yield new_pos.copy()
                new_pos += direction

    def displayAccess(self, index=-1):
        for pos in self.possible_moves_from(
                self.action_capacitor[index]):
            self.display_board.grid.set(pos, 6)

    def unDisplayAccess(self):
        for i in range(self.N):
            for j in range(self.N):
                grid_pos = self.display_board.grid.at(Pos2D(i, j))
                if grid_pos == 6:
                    self.display_board.grid.set(Pos2D(i, j), EMPTY)

    def init_vars(self):
        """
        Initialise the game related variables.
        :return: None
        """
        self.N = 6
        self.pos_black = ['c4']
        self.pos_white = ['a1']
        self.pos_arrows = []
        self.start_pos_black = self.pos_black
        self.start_pos_white = self.pos_white
        self.start_pos_arrows = self.pos_arrows
        # self.pos_arrows = ['b1', 'b2', 'b3', 'a3']
        self.amazons_game = Amazons(self.N, self.pos_black,
                                    self.pos_white,
                                    self.pos_arrows)
        self.board = self.amazons_game.board
        self.display_board = self.board

        self.time_interval = 0

        self.active_button = False
        self.record = False
        self.rewatch = False

    @staticmethod
    def make_player(text, player_id, board):
        """
        Create a player depending on the given parameter.
        :param text: either 'AI' or 'Human'
        :param player_id: id of the player to create
        :param board: an instance of the class `Board`
        :return: an instance of the class `Player`
        :raise: `ValueError` if text does not match correct inputs
        """
        if text == 'Tournament AI':
            return TournoiAIPlayer(board, player_id)

        elif text == 'Minimax AI':
            return AIPlayer(board, player_id)

        elif text == 'GUI AI':
            return guiAI.GUIAIPlayer(board, player_id)

        elif text == 'Human':
            return HumanPlayer(board, player_id)
        else:
            raise ValueError('Only \'AI\' and \'Human\' are '
                             'valid player types')

    def record_game(self):
        self.record = True
        self.record_button.setText("Recording")

    def reset(self, to_start=False):
        if to_start:
            self.amazons_game = Amazons(self.N,
                                        self.start_pos_black,
                                        self.start_pos_white,
                                        self.start_pos_arrows)
        else:
            self.amazons_game = Amazons(self.N, self.pos_black,
                                        self.pos_white,
                                        self.pos_arrows)
        self.board = self.amazons_game.board
        self.display_board = self.board
        self.canvas.reset(self.display_board,
                          self.N,
                          self.width,
                          self.height)
        self.canvas.update()

    def start_game(self):
        """
        Callback of Clicked event on the start/restart button.
        :return: None
        """
        self.cancel_active_button()
        if self.cb_timer.currentText() == "Timer":
            self.timer = True
        else:
            self.timer = False

        if self.rewatch:
            self.player_1 = App.make_player(
                "AI",
                1,
                self.board)
            self.player_2 = App.make_player(
                "AI",
                2,
                self.board)
            self.actions_history_current_index = 0
            self.time_interval = 999

        else:
            self.players_groupbox.setVisible(False)
            self.board_options_groupbox.setVisible(False)
            if self.start_button.text == 'Restart':
                self.reset(to_start=True)

            else:
                self.start_pos_black = self.pos_black
                self.start_pos_white = self.pos_white
                self.start_pos_arrows = self.pos_arrows

            self.player_1 = App.make_player(
                self.cb_player1.currentText(),
                0,
                self.board)
            self.player_2 = App.make_player(
                self.cb_player2.currentText(),
                1,
                self.board)
        self.start_button.setText('Restart')

        self.current_player = self.player_2
        self.waiting_player = self.player_1

        self.toggle_players()  # So that player 1 starts

    def toggle_players(self):
        """
        Swap current player and waiting player.
        :return: None
        """
        self.display_board = self.board
        self.canvas.reset(self.display_board, self.N, self.width,
                          self.height)
        self.current_player.not_your_turn()
        if self.amazons_game.is_over():
            self.exhibit_end_of_game()
            return
        self.current_player, self.waiting_player = self.waiting_player, self.current_player
        self.current_player.your_turn()
        if isinstance(self.current_player, AIPlayer):
            if self.rewatch:
                action = self.actions_history[
                    self.actions_history_current_index]
                self.actions_history_current_index += 1
                self.board.act(action, self.current_player.player_id)
            else:
                if self.timer:
                    timer_start = time.time()
                    self.current_player.play()
                    timer_stop = time.time()
                    action_time = timer_stop - timer_start
                    if action_time < 2:  # todo 2s
                        self.timer_display_label.setText('Played in:'
                        + str(action_time) + 'seconds!')
                    else:
                        self.exhibit_end_of_game(timeout=True)
                        return
                else:
                    self.current_player.play()
            QTimer.singleShot(self.time_interval, self.toggle_players)
        else:
            self.action_capacitor = []

    def exhibit_end_of_game(self, timeout=False):
        """
        Show that the game is over and display the winner.
        """

        if self.record:
            name = str(datetime.datetime.now().strftime("%Y-%m-%d-"
                                                        "%H-%M-%S"))
            f = open(name + ".txt", "x")
            f.write(str(self.N) + "\n")
            for line in [self.start_pos_black, self.start_pos_white,
                         self.start_pos_arrows]:
                if not line:
                    f.write("\n")

                f.write(",".join(line))
                f.write("\n")
            for action in self.board.history:
                f.write(str(action) + "\n")
            f.close()
        if timeout:
            popup = WinnerPopup(self.current_player.player_id, self,
                                timeout=True)
        else:
            popup = WinnerPopup(self.amazons_game.get_winner_id(), self)
        popup.exec_()  # Use exec_ instead of show to block main
        # window
        self.current_player = None
        self.waiting_player = None
        self.record_button.setVisible(True)
        self.players_groupbox.setVisible(True)
        self.board_options_groupbox.setVisible(True)

    def exhibit_recorded_games(self):
        replay_fd = QFileDialog()
        replay_fd.exec_()
        self.filename = replay_fd.selectedFiles()[0]
        self.N, \
        self.pos_white, \
        self.pos_black, \
        self.pos_arrows, \
        self.actions_history = amazons.read_file(self.filename,
                                                 history=True)
        l = []
        player = 0
        for positions in self.actions_history:
            l.append(Action(Pos2D(positions[0][1], positions[0][0]),
                            Pos2D(positions[1][1], positions[1][0]),
                            Pos2D(positions[2][1], positions[2][0]),
                            player))
            player = abs(player - 1)
        self.actions_history = l
        self.reset()
        self.players_groupbox.setVisible(False)
        self.board_options_groupbox.setVisible(False)
        self.time_slider.setVisible(False)
        self.rewatch = True


class WinnerPopup(QDialog):
    """
    Popup displaying the winner(s) of the game
    """

    def __init__(self, winner, parent, timeout=False):
        """
        Constructor of class `WinnerPopup`
        :param winner: a list of winners
        :param parent: the parent Qt widget
        """
        super().__init__(parent)
        if timeout:
            text = f'Player {abs(winner - 1) + 1} too slow!\n' \
                   f'Player {winner + 1} won!'
        else:
            text = f'Player {winner} won!'
        self.setFixedSize(QSize(500, 100))
        self.label = QLabel(text, self)
        self.label.setFont(QFont("Calibri", 20, QFont.Bold))
        label_width = self.label.fontMetrics().boundingRect(
            self.label.text()).width()
        label_height = self.label.fontMetrics().boundingRect(
            self.label.text()).height()
        self.label.move((self.width() - label_width) / 2,
                        (self.height() - label_height) / 2)


class Canvas(QWidget):
    """
    Qt-compatible widget representing the canvas on which the board
    is drawn repeatedly.
    :attribute board:
    """

    def __init__(self, display_board, N, main_window_width,
                 main_window_height,
                 parent=None):
        """
        Constructor of the class `Canvas` :param board: instance of
        the class `Board` that shall be represented :param parent:
        the parent Qt widget
        """
        super().__init__(parent=parent, flags=Qt.WindowFlags())

        self.reset(display_board, N, main_window_width,
                   main_window_height)

    def reset(self, display_board, N, main_window_width,
              main_window_height):
        self.N = N
        self.width = 4 * main_window_width / 5
        self.height = 9 * main_window_height / 10
        self.setFixedSize(QSize(self.width, self.height))
        self.cell_size = self.height // (self.N)
        self.display_grid = display_board.grid

        self.update()

    def pos2rowcol(self, x, y):
        """
        Transform a (x, y) position on the canvas into a cell number.
        :param x: x position on the canvas
        :param y: y position on the canvas
        :return: tuple (row_id, col_idx)
        """
        row =int(y / self.cell_size)
        col =int(x / self.cell_size)
        return row, col

    def paintEvent(self, event=None):
        """
        Callback of the Update event on the canvas.
        :param event: ignored
        """
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def draw(self, qp):
        """
        Draw the board onto the canvas.
        :param qp: instance of class `QPainter`
        """
        self.draw_grid_debug(qp)
        # associated color to each possible value of the board cells:
        # empty is drawn *white*, arrow is drawn black, player 1 is
        # drawn *yellow*,
        # player 2 is drawn *red*
        colors = [Qt.darkGreen, Qt.darkRed, Qt.white, Qt.black,
                  Qt.green,
                  Qt.red,
                  Qt.cyan]
        qp.setPen(Qt.black)
        for row in range(self.N):
            # First draw the rectangle of the current row
            y = 0 + row * self.cell_size
            x = 0
            # (x, y) represents the middle of the left cell of
            # considered row
            """
            qp.drawRect(
                x - cell_size // 2 + 5,
                y - cell_size // 2 + 5,
                self.N * cell_size - 10,
                cell_size - 10
            )"""
            # Then draw each circle within that row
            for col in range(self.N):
                qp.setBrush(
                    colors[self.display_grid.at(Pos2D(row, col))])
                qp.drawEllipse(
                    x,  # - self.cell_size / 2,
                    y,  # - self.cell_size / 2,
                    8 * self.cell_size / 9,
                    8 * self.cell_size / 9
                )
                x += self.cell_size

    def draw_grid_debug(self, qp):
        """
        Draw debug lines on the canvas. Only used when adapting the size of the cells/rows.
        :param qp: instance of class `QPainter`
        """
        if not GRID_DEBUG:
            return

        qp.setPen(Qt.red)
        x = 0
        for i in range(self.N):
            x += self.cell_size
            qp.drawLine(x, 0, x, self.height)
        y = 0
        for i in range(self.N):
            y += self.cell_size
            qp.drawLine(0, y, self.width, y)
