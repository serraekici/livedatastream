class LineStyle:
    def __init__(self, line_style_combobox):
        self.line_style_combobox = line_style_combobox

    def get_line_style(self):
        styles = {
            'Solid': '-',
            'Dashed': '--',
            'Dotted': ':',
            'Dashdot': '-.'
        }
        return styles.get(self.line_style_combobox.get(), '-')
