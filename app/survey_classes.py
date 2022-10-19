from django.utils.html import mark_safe

count = 0


class Question:
    """Object to be interpreted by Survey class form"""

    def __init__(
        self, question, type, required=True,
        label=None, choices=None, help=None, scale=None,
        max_digits=2, decimal_places=0, date_range=range(1940, 2019),
    ):
        self.question = question
        self.type = type
        self.required = required
        self.choices = choices
        self.help = help
        self.scale = scale
        self.attrs = {}
        self.max_digits = max_digits
        self.decimal_places = decimal_places
        self.date_range = date_range

        if label != None:
            self.label = mark_safe(label)
        else:
            self.label = f'{self.question} *' if self.required else self.question

    def key(self):
        """Prints nice version of question"""
        choices = ""
        if self.choices:
            temp = []
            for choice in self.choices:
                if choice[1]:
                    temp.append(f" > {choice[1]}")
            choices = "\n".join(temp)
        summary = f"{self.question}. {self.label}\n{choices}"
        return print(summary)


class Divider:
    def __init__(self, label=None, id='divider'):
        global count
        count += 1
        self.question = f"divider{f'-text{count}' if id != 'divider' else count}"
        self.type = 'divider'
        if not label:
            self.label = mark_safe("</table><br><table>")
            self.question = f"break{count}"
        if id == 'form-text':
            self.label = mark_safe(f"<div class='form-text'>{label}</div>")
        else:
            self.label = mark_safe(label)
