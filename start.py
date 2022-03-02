from datetime import datetime

from prettytable import PrettyTable
from pydantic import ValidationError

from model import BankStatement, DepositWithdraw


class Bank:
    operations = []
    clients = {}

    def deposit_handler(self, data):
        date = datetime.now()
        balance = self.clients.get(data.client, 0)
        self.clients[data.client] = balance + data.amount
        self.operations.append({'command': 'deposit', 'date': date, **data.dict()})
        return 'Deposit operation was successful!'

    def withdraw_handler(self, data):
        date = datetime.now()
        balance = self.clients.get(data.client, 0)
        if balance < data.amount:
            return 'Withdrawal operation was unsuccessful!\nBalance is too low.'
        self.clients[data.client] = balance - data.amount
        self.operations.append({'command': 'withdraw', 'date': date, **data.dict()})
        return 'Withdrawal operation was successful!'

    def show_bank_statement(self, data):
        table = PrettyTable()
        table.field_names = ['Date', 'Desctiption', 'Withdrawals', 'Deposits', 'Balance']
        prev_balance = 0
        prev_flag = 1
        balance = 0
        d, w = 0, 0
        for o in self.operations:
            if (data.since <= o['date'] <= data.till) and (o['client'] == data.client):
                if prev_flag == 1:
                    table.add_row(['', 'Previous balance', '', '', "${:.2f}".format(prev_balance)])
                    balance = prev_balance
                prev_flag = 0
                d += o['amount'] if o['command'] == 'deposit' else 0
                w += o['amount'] if o['command'] == 'withdraw' else 0
                balance += o['amount'] if o['command'] == 'deposit' else 0
                balance -= o['amount'] if o['command'] == 'withdraw' else 0

                table.add_row([
                    o['date'].strftime("%Y-%m-%d %H:%M:%S"),
                    o['description'],
                    f"${o['amount']}" if o['command'] == 'withdraw' else '',
                    f"${o['amount']}" if o['command'] == 'deposit' else '',
                    "${:.2f}".format(balance)
                ])
            elif (data.since > o['date']) and (o['client'] == data.client):
                prev_balance += o['amount'] if o['command'] == 'deposit' else 0
                prev_balance -= o['amount'] if o['command'] == 'withdraw' else 0
        table.add_row(['', 'Totals', "${:.2f}".format(w), "${:.2f}".format(d), "${:.2f}".format(balance)])

        return table


if __name__ == '__main__':
    print('''
    Service started!
    Commands:
    • deposit 
        required arguments: client (str), amount (float), description (str)
        example: 
        deposit --client="John Jones" --amount=100.124 --description="ATM Deposit"
    • withdraw 
        required arguments: client (str), amount (float), description (str)
        example: 
        withdraw --client="John Jones" --amount=100 --description="ATM Withdrawal"
    • show_bank_statement 
        required arguments: client (str), since (str, dateformat %Y-%m-%d %H:%M:%S), till (str, dateformat %Y-%m-%d %H:%M:%S)
        example: 
        show_bank_statement --client="John Jones" --since="2022-03-01 00:00:00" --till="2024-01-01 00:00:00"
    ''')

    while True:
        bank = Bank()
        command = input()
        commands = command.split(' -')
        func = commands.pop(0)
        trim_args = {}
        for comm in commands:
            k = comm.split('=')[0][1:]
            v = comm.split('=')[1].replace('"', '')
            trim_args[k] = v
        try:
            if func == 'deposit':
                deposit = DepositWithdraw(**trim_args)
                deposit.amount = float("{0:.2f}".format(deposit.amount))
                print(bank.deposit_handler(deposit))
            elif func == 'withdraw':
                withdraw = DepositWithdraw(**trim_args)
                withdraw.amount = float("{0:.2f}".format(withdraw.amount))
                print(bank.withdraw_handler(withdraw))
            elif func == 'show_bank_statement':
                trim_args['since'] = datetime.strptime(trim_args.get('since', None), "%Y-%m-%d %H:%M:%S")
                trim_args['till'] = datetime.strptime(trim_args.get('till', None), "%Y-%m-%d %H:%M:%S")
                statement = BankStatement(**trim_args)
                print(bank.show_bank_statement(statement))
            elif func == 'exit':
                print('Service stopped!')
                break
        except (ValidationError, ValueError) as e:
            print(e)
