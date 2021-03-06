#!/usr/bin/env python3
# encoding: utf-8
import curses
import npyscreen as nps
import logging

class GridMulTitles(nps.SimpleGrid):
    _col_widgets = nps.Textfield
    def __init__(self, screen, col_titles, *args, **keywords):
        if col_titles:
            self.col_titles = col_titles
        else:
            self.col_titles = []

        self.need_line_no = True
        GridMulTitles.additional_y_offset = len(self.col_titles) + 1
        super(GridMulTitles, self).__init__(screen, *args, **keywords)
    
    def make_contained_widgets(self):
        super(GridMulTitles, self).make_contained_widgets()
        self._my_col_titles = []

        for y_offset in range(len(self.col_titles)):
            self._my_col_titles.append([])
            for title_cell in range(self.columns):
                x_offset = title_cell * (self._column_width+self.col_margin)
                self._my_col_titles[-1].append(self._col_widgets(self.parent,
                    rely=self.rely + y_offset, relx = self.relx + x_offset,
                    width=self._column_width, height=1))

    def set_up_handlers(self):
        super(GridMulTitles, self).set_up_handlers()
        self.handlers.update({
            "0" : self.h_move_cell_beg,
            "$" : self.h_move_cell_end,
            "H" : self.h_move_cell_beg,
            "L" : self.h_move_cell_end,
            "J" : self.h_move_page_down,
            "K" : self.h_move_page_up,
            "^F": self.h_move_page_down,
            "^B": self.h_move_page_up,
            "n": self.h_show_line_no,          
        })

    def custom_print_cell(self, cell, value):
        if -1 == cell.grid_current_value_index:
            return

        row, col = cell.grid_current_value_index
        if 0 == col and self.need_line_no:
            cell.value = f'{row}: {value}'
        #logging.info(f'[{row},{col}] = {cell.value}')
    
    def highlight_or_not(self, r, c):
        if self.edit_cell is None or 2 != len(self.edit_cell):
            return False
        
        if self.edit_cell[1] != c:
            return False

        if 1 == len(self.col_titles):
            return True
        
        head_prefix = self.col_titles[r][0].split(':')[0]
        cell_value = str(self.values[self.edit_cell[0]][0])
        return cell_value.startswith(head_prefix)

    def update(self, clear=True):
        super(GridMulTitles, self).update(clear = True)
        for r in range(len(self.col_titles)):
            _title_counter = 0
            for title_cell in self._my_col_titles[r]:
                try:
                    c = _title_counter+self.begin_col_display_at
                    if self.highlight_or_not(r, c):
                        title_cell.highlight = True
                    else:
                        title_cell.highlight = False
                    title_text = self.col_titles[r][c]
                    #logging.info(f'{r},{self.begin_col_display_at},{_title_counter}:{title_text}')
                except IndexError:
                    title_text = None
                self.update_title_cell(title_cell, title_text)
                _title_counter+=1
            
        self.parent.curses_pad.hline(self.rely+len(self.col_titles), self.relx, curses.ACS_HLINE, self.max_width+3*self.col_margin)
    
    def update_title_cell(self, cell, cell_title):
        cell.value = cell_title
        cell.update()

    def h_move_cell_beg(self, inpt):
        self.edit_cell[1] -= self.columns
        if self.edit_cell[1] < 0:
            self.edit_cell[1] = 0

        self.begin_col_display_at = (self.edit_cell[1]//self.columns)*self.columns
        self.on_select(inpt)
    
    def h_move_cell_end(self, inpt):
        self.edit_cell[1] += self.columns
        if self.edit_cell[1] >= len(self.values[0]):
            self.edit_cell[1] = 0

        self.begin_col_display_at = (self.edit_cell[1]//self.columns)*self.columns
        self.on_select(inpt)

    def h_show_beginning(self, inpt):
        self.begin_row_display_at = 0
        self.edit_cell = [0, self.edit_cell[1]]
        self.on_select(inpt)

    def h_show_end(self, inpt):
        self.edit_cell = [len(self.values) - 1 , self.edit_cell[1]]
        self.ensure_cursor_on_display_down_right()
        self.on_select(inpt)

    def h_show_line_no(self, inpt):
        self.need_line_no = False if self.need_line_no else True
        
