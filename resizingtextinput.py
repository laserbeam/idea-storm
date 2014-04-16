from kivy.properties import *
from kivy.uix.textinput import TextInput, FL_IS_NEWLINE
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.utils import boundary


class ResizingTextInput(TextInput):
    min_width = NumericProperty(100.)
    max_width = NumericProperty(400.)
    halign = OptionProperty('left', options=['left', 'center'])
    # 'right' looks wrong... due to some spaces at the ends of the labels

    def __init__(self, **kwargs):
        super(ResizingTextInput, self).__init__(**kwargs)
        self.bind(text=self._schedule_widget_resize,
                  line_height=self._schedule_widget_resize,
                  line_spacing=self._schedule_widget_resize,
                  padding=self._schedule_widget_resize)
        Clock.schedule_once(self._first_resize, -1)
        self._line_offsets = []

    # Just copied from TextInput and set width to a fixed size
    def _split_smart(self, text):
        # Do a "smart" split. If autowidth or autosize is set,
        # we are not doing smart split, just a split on line break.
        # Otherwise, we are trying to split as soon as possible, to prevent
        # overflow on the widget.

        # depend of the options, split the text on line, or word
        if not self.multiline:
            lines = text.split(u'\n')
            lines_flags = [0] + [FL_IS_NEWLINE] * (len(lines) - 1)
            return lines, lines_flags

        # no autosize, do wordwrap.
        x = flags = 0
        line = []
        lines = []
        lines_flags = []
        _join = u''.join
        lines_append, lines_flags_append = lines.append, lines_flags.append
        padding_left = self.padding[0]
        padding_right = self.padding[2]
        # CHANGE MADE HERE!
        width = self.max_width - padding_left - padding_right
        text_width = self._get_text_width
        _tab_width, _label_cached = self.tab_width, self._label_cached

        for word in self._tokenize(text):
            width = max(width, text_width(word, _tab_width, _label_cached))
        # try to add each word on current line.
        for word in self._tokenize(text):
            is_newline = (word == u'\n')
            w = text_width(word, _tab_width, _label_cached)
            # if we have more than the width, or if it's a newline,
            # push the current line, and create a new one
            if (x + w > width and line) or is_newline:
                lines_append(_join(line))
                lines_flags_append(flags)
                flags = 0
                line = []
                x = 0
            if is_newline:
                flags |= FL_IS_NEWLINE
            else:
                x += w
                line.append(word)
        if line or flags & FL_IS_NEWLINE:
            lines_append(_join(line))
            lines_flags_append(flags)

        return lines, lines_flags

    def cursor_offset(self):
        '''Get the cursor x offset on the current line.
        '''
        offset = 0
        row = self.cursor_row
        col = self.cursor_col
        _lines = self._lines
        if col and row < len(_lines):
            offset = self._get_text_width(
                _lines[row][:col], self.tab_width,
                self._label_cached)
        if len(self._line_offsets) > self.cursor_row:
            offset = offset + self._line_offsets[self.cursor_row]
        return offset

    def get_cursor_from_xy(self, x, y):
        '''Return the (row, col) of the cursor from an (x, y) position.
        '''
        padding_left = self.padding[0]
        padding_top = self.padding[1]
        l = self._lines
        dy = self.line_height + self.line_spacing
        cx = x - self.x
        scrl_y = self.scroll_y
        scrl_x = self.scroll_x
        scrl_y = scrl_y / dy if scrl_y > 0 else 0
        cy = (self.top - padding_top + scrl_y * dy) - y
        cy = int(boundary(round(cy / dy - 0.5), 0, len(l) - 1))
        cx = cx - self._line_offsets[cy]
        dcx = 0
        _get_text_width = self._get_text_width
        _tab_width = self.tab_width
        _label_cached = self._label_cached
        for i in range(1, len(l[cy]) + 1):
            if _get_text_width(l[cy][:i],
                               _tab_width,
                               _label_cached) + padding_left >= cx + scrl_x:
                break
            dcx = i
        cx = dcx
        return cx, cy

    def _update_graphics(self, *largs):
# Update all the graphics according to the current internal values.
        #
        # This is a little bit complex, cause we have to :
        #     - handle scroll_x
        #     - handle padding
        #     - create rectangle for the lines matching the viewport
        #     - crop the texture coordinates to match the viewport
        #
        # This is the first step of graphics, the second is the selection.

        self.canvas.clear()
        add = self.canvas.add

        lh = self.line_height
        dy = lh + self.line_spacing

        # adjust view if the cursor is going outside the bounds
        sx = self.scroll_x
        sy = self.scroll_y

        # draw labels
        if not self.focus and (not self._lines or (
                not self._lines[0] and len(self._lines) == 1)):
            rects = self._hint_text_rects
            labels = self._hint_text_labels
            lines = self._hint_text_lines
        else:
            rects = self._lines_rects
            labels = self._lines_labels
            lines = self._lines
        self._line_offsets = [0] * len(lines)
        padding_left, padding_top, padding_right, padding_bottom = self.padding
        x = self.x + padding_left
        y = self.top - padding_top + sy
        miny = self.y + padding_bottom
        maxy = self.top - padding_top
        max_line_width = self.width - padding_left - padding_right
        for line_num, value in enumerate(lines):
            if miny <= y <= maxy + dy:
                texture = labels[line_num]
                if not texture:
                    y -= dy
                    continue
                size = list(texture.size)
                texc = texture.tex_coords[:]

                # calcul coordinate
                viewport_pos = sx, 0
                vw = self.width - padding_left - padding_right
                vh = self.height - padding_top - padding_bottom
                tw, th = list(map(float, size))
                oh, ow = tch, tcw = texc[1:3]
                tcx, tcy = 0, 0

                # adjust size/texcoord according to viewport
                if vw < tw:
                    tcw = (vw / tw) * tcw
                    size[0] = vw
                if vh < th:
                    tch = (vh / th) * tch
                    size[1] = vh
                if viewport_pos:
                    tcx, tcy = viewport_pos
                    tcx = tcx / tw * (ow)
                    tcy = tcy / th * oh

                # cropping
                mlh = lh
                if y > maxy:
                    vh = (maxy - y + lh)
                    tch = (vh / float(lh)) * oh
                    tcy = oh - tch
                    size[1] = vh
                if y - lh < miny:
                    diff = miny - (y - lh)
                    y += diff
                    vh = lh - diff
                    tch = (vh / float(lh)) * oh
                    size[1] = vh

                texc = (
                    tcx,
                    tcy + tch,
                    tcx + tcw,
                    tcy + tch,
                    tcx + tcw,
                    tcy,
                    tcx,
                    tcy)

                offset = 0
                if self.halign == 'center':
                    offset = (max_line_width - size[0])/2
                elif self.halign == 'right':
                    offset = max_line_width - size[0]
                print size[0], offset
                self._line_offsets[line_num] = offset
                # add rectangle.
                r = rects[line_num]
                r.pos = int(x + offset), int(y - mlh)
                r.size = size
                r.texture = texture
                r.tex_coords = texc
                add(r)

            y -= dy

        self._update_graphics_selection()
        self._schedule_widget_resize()

    def _schedule_widget_resize(self, *arg):
        Clock.unschedule(self._update_widget_size)
        Clock.schedule_once(self._update_widget_size, 0)

    def _first_resize(self, *arg):
        self._update_widget_size()

    def _update_widget_size(self, *arg):
        rects = self._lines_rects
        lines = self._lines_labels
        lh = self.line_height + self.line_spacing
        self.height = self.line_height + (len(lines)-1) * lh
        if len(rects) > 0:
            w = max(l.size[0] for l in rects)
        else:
            w = 0
        self.width = max(w, self.min_width)
        self.cursor = self.get_cursor_from_index(self.cursor_index())
        # print 'post_trigger', self.cursor_index()

Factory.register('ResizingTextInput', cls=ResizingTextInput)
