class Display:

    def __init__(self):
        return

    def show(self, text, end='\n'):
        if isinstance(text, list):
            for line in text:
                print(f'\t| {line}', end=end)
        else:
            print(f'\t| {text}', end=end)

    def ask(self, question_context, question):

        print("")  # Go to new line
        self.show('--------------[ Question ] --------------------')
        if question_context is not None:
            self.show(question_context)
        self.show(f'{question} :', end='')
        answer = input()
        self.show('-----------------------------------------------')
        return answer
