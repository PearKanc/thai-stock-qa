import click
from src.retrieval import answer_question

@click.command()
@click.option('--question', '-q', prompt='ป้อนคำถามของคุณ', help='คำถามที่ต้องการถาม')
def main(question):
    answer = answer_question(question)
    click.echo("\n" + "="*50)
    click.echo(answer)

if __name__ == '__main__':
    main()