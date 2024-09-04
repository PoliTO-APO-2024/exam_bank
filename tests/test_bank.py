import unittest
import inspect
from bank.manager import Bank
from bank.account import BankAccount
from bank.exceptions import BankException

class TestR0(unittest.TestCase):
    
    def test_abstract(self):
        self.assertTrue(inspect.isabstract(BankAccount))


class TestR1(unittest.TestCase):

    def setUp(self):
        self._bank = Bank()

    def test_add_client(self):
        client_ids = []
        client_ids.append(self._bank.add_client("Name1", 18))
        client_ids.append(self._bank.add_client("Name2", 29))
        client_ids.append(self._bank.add_client("Name3", 51))
        self.assertEqual([1000, 1001, 1002], client_ids)

    def test_add_client_multiple_banks(self):
        client_ids = []
        client_ids.append(self._bank.add_client("Name1", 18))
        client_ids.append(self._bank.add_client("Name2", 29))
        client_ids.append(self._bank.add_client("Name3", 51))
        self.assertEqual([1000, 1001, 1002], client_ids)

        bank_2 = Bank()
        client_ids = []
        client_ids.append(bank_2.add_client("Name1", 18))
        client_ids.append(bank_2.add_client("Name2", 29))
        client_ids.append(bank_2.add_client("Name3", 51))
        self.assertEqual([1000, 1001, 1002], client_ids)

    def test_get_client(self):
        client_ids = []
        client_ids.append(self._bank.add_client("Name1", 18))
        client_ids.append(self._bank.add_client("Name2", 29))

        self.assertEqual("1001,Name2,29", self._bank.get_client(1001))
        self.assertEqual("1000,Name1,18", self._bank.get_client(1000))

    def test_get_incentives_no_thresh(self):
        self._bank.add_incentive("Inc1", 100)
        self._bank.add_incentive("Inc2", 15)
        self._bank.add_incentive("Inc3", 52)
        self.assertEqual({"Inc1", "Inc2", "Inc3"}, set(self._bank.get_incentives(0)))

    def test_get_incentives_thresh(self):
        self._bank.add_incentive("Inc1", 100)
        self._bank.add_incentive("Inc2", 15)
        self._bank.add_incentive("Inc3", 52)
        self.assertEqual({"Inc1", "Inc3"}, set(self._bank.get_incentives(20)))        

class TestR2(unittest.TestCase):

    def setUp(self):
        self._bank = Bank()
        self._bank.add_client("Name1", 18)
        self._bank.add_client("Name2", 29)
        self._bank.add_client("Name3", 51)

    def test_account_properties(self):
        normal = self._bank.add_normal_account("aa11", 15000, 1000)
        deposit = self._bank.add_deposit_account("bb22", 8000, 1001)
        escrow = self._bank.add_escrow_account("cc33", 9000, 1002, "aa11")

        self.assertEqual(["aa11", 15000], [normal.iban, normal.balance])
        self.assertEqual(["bb22", 8000], [deposit.iban, deposit.balance])
        self.assertEqual(["cc33", 9000], [escrow.iban, escrow.balance])

    def test_account_duration(self):
        normal = self._bank.add_normal_account("aa11", 15000, 1000)
        deposit = self._bank.add_deposit_account("bb22", 8000, 1001)
        escrow = self._bank.add_escrow_account("cc33", 9000, 1002, "aa11")

        self.assertEqual(None, normal.duration)
        self.assertEqual(None, deposit.duration)
        self.assertEqual(3, escrow.duration)

    def test_withdrawal(self):
        normal = self._bank.add_normal_account("aa11", 15000, 1000)
        deposit = self._bank.add_deposit_account("bb22", 8000, 1001)

        normal.withdraw(875)
        deposit.withdraw(875)

        self.assertEqual(15000 - 875, normal.balance)
        self.assertEqual(8000 - 875, deposit.balance)

    def test_add_funds(self):
        normal = self._bank.add_normal_account("aa11", 15000, 1000)
        deposit = self._bank.add_deposit_account("bb22", 8000, 1001)

        normal.add_funds(875)
        deposit.add_funds(875)

        self.assertEqual(15000 + 875, normal.balance)
        self.assertEqual(8000 + 875, deposit.balance)        

    def test_deposit_exceptions(self):
        deposit = self._bank.add_deposit_account("bb22", 150000, 1001)
        
        deposit.withdraw(1000)
        self.assertRaises(BankException, deposit.withdraw, 120000)

    def test_escrow_exceptions(self):
        normal = self._bank.add_normal_account("aa11", 15000, 1000)
        escrow = self._bank.add_escrow_account("cc33", 9000, 1002, "aa11")

        self.assertRaises(BankException, escrow.withdraw, 1400)
        self.assertRaises(BankException, escrow.add_funds, 1400)


class TestR3(unittest.TestCase):
    def setUp(self) -> None:
        self._bank = Bank()
        self._bank.add_client("Name1", 18)
        self._bank.add_client("Name2", 29)
        self._bank.add_client("Name3", 51)

    def test_get_client_of_account(self):
        account_1 = self._bank.add_normal_account("aa11", 1500, 1000)
        account_2 = self._bank.add_normal_account("bb22", 1500, 1001)
        account_3 = self._bank.add_normal_account("cc33", 1500, 1002)

        self.assertEqual(1000, self._bank.get_client_of_account("aa11"))
        self.assertEqual(1001, self._bank.get_client_of_account("bb22"))
        self.assertEqual(1002, self._bank.get_client_of_account("cc33"))

    def test_get_accounts_of_client(self):
        account_1 = self._bank.add_normal_account("aa11", 1500, 1000)
        account_2 = self._bank.add_normal_account("bb22", 1500, 1001)
        account_3 = self._bank.add_normal_account("cc33", 1500, 1002)
        account_4 = self._bank.add_normal_account("dd44", 1500, 1001)
        account_5 = self._bank.add_normal_account("ee55", 1500, 1002)
        account_6 = self._bank.add_normal_account("ff66", 1500, 1002)

        accounts_client_1 = self._bank.get_accounts_of_client(1000)
        accounts_client_2 = self._bank.get_accounts_of_client(1001)
        accounts_client_3 = self._bank.get_accounts_of_client(1002)

        self.assertEqual(["aa11"], [a.iban for a in self._bank.get_accounts_of_client(1000)])
        self.assertEqual(["bb22", "dd44"],  sorted([a.iban for a in self._bank.get_accounts_of_client(1001)]))
        self.assertEqual(["cc33", "ee55", "ff66"],  sorted([a.iban for a in self._bank.get_accounts_of_client(1002)]))

    def test_get_client_and_accounts(self):        
        account_1 = self._bank.add_normal_account("aa11", 1500, 1001)
        account_2 = self._bank.add_deposit_account("bb22", 1500, 1001)
        account_3 = self._bank.add_escrow_account("cc33", 1500, 1002, "aa11")
        account_4 = self._bank.add_normal_account("dd44", 1500, 1002)

        self.assertEqual(1001, self._bank.get_client_of_account("aa11"))
        self.assertEqual(1001, self._bank.get_client_of_account("bb22"))
        self.assertEqual(1002, self._bank.get_client_of_account("cc33"))
        self.assertEqual(1002, self._bank.get_client_of_account("dd44"))

        self.assertEqual(["aa11", "bb22"],  sorted([a.iban for a in self._bank.get_accounts_of_client(1001)]))
        self.assertEqual(["cc33", "dd44"],  sorted([a.iban for a in self._bank.get_accounts_of_client(1002)]))


    def test_assign_incentives(self):
        self._bank.add_incentive("Inc1", 100)
        self._bank.add_incentive("Inc2", 15)
        self._bank.add_incentive("Inc3", 52)
        self._bank.add_incentive("Inc4", 100)
        self._bank.add_incentive("Inc5", 15)

        self._bank.add_normal_account("aa11", 1500, 1000)
        self._bank.add_deposit_account("bb22", 1500, 1001)
        self._bank.add_escrow_account("cc33", 1500, 1002, "aa11")

        self._bank.assign_incentives(("aa11", "Inc1"), ("bb22", "Inc2"), ("cc33", "Inc3"), ("aa11", "Inc4"), ("cc33", "Inc5"))
        
        self.assertEqual(["Inc1", "Inc4"], sorted(self._bank.get_account_incentives("aa11")))
        self.assertEqual(["Inc2"], sorted(self._bank.get_account_incentives("bb22")))
        self.assertEqual(["Inc3", "Inc5"], sorted(self._bank.get_account_incentives("cc33")))


    def test_assign_incentives_duplicate(self):
        self._bank.add_incentive("Inc1", 100)
        self._bank.add_incentive("Inc2", 15)
        self._bank.add_incentive("Inc3", 52)
        self._bank.add_incentive("Inc4", 100)
        self._bank.add_incentive("Inc5", 100)

        self._bank.add_normal_account("aa11", 1500, 1000)
        self._bank.add_deposit_account("bb22", 1500, 1001)

        self._bank.assign_incentives(("aa11", "Inc1"), ("bb22", "Inc2"), ("aa11", "Inc1"), ("bb22", "Inc3"), ("aa11", "Inc4"), ("bb22", "Inc2"))
        
        self.assertEqual(["Inc1", "Inc4"], sorted(self._bank.get_account_incentives("aa11")))
        self.assertEqual(["Inc2", "Inc3"], sorted(self._bank.get_account_incentives("bb22")))


class TestR4(unittest.TestCase):

    def setUp(self):
        self._bank = Bank()
        self._bank.add_client("Name1", 18)
        self._bank.add_client("Name2", 29)
        self._bank.add_client("Name3", 51)

        self._account_1 = self._bank.add_normal_account("aa11", 1500, 1000)
        self._account_2 = self._bank.add_deposit_account("bb22", 1500, 1001)
        self._account_3 = self._bank.add_normal_account("cc33", 1500, 1001)
    
    def test_transfer_money(self):
        self._bank.transfer_money("aa11", "bb22", 500)
        self.assertEqual(1000, self._account_1.balance)
        self.assertEqual(2000, self._account_2.balance)       

    def test_transfer_money_exception(self):
        self._bank.transfer_money("bb22", "aa11", 100)
        self.assertRaises(BankException, self._bank.transfer_money, "aa11", "bb22", 2000)

    def test_close_account(self):
        self._bank.close_account("bb22", "cc33")
        self.assertEqual(3000, self._account_3.balance)
        self.assertEqual(["cc33"], [a.iban for a in self._bank.get_accounts_of_client(1001)])

    def test_close_account_exception(self):
        self._bank.close_account("bb22", "cc33")
        self.assertRaises(BankException, self._bank.close_account, "cc33", "aa11")


class TestR5(unittest.TestCase):
    def setUp(self):
        self._bank = Bank()
        self._bank.add_client("Name1", 57)

        self._account_1 = self._bank.add_normal_account("aa11", 1500, 1000)
        self._account_2 = self._bank.add_deposit_account("bb22", 1500, 1000)
        self._account_3 = self._bank.add_escrow_account("cc33", 1500, 1000, "aa11")

    def test_simulate_accounts(self):
        self.assertIsNone(self._account_1.simulate())
        self.assertIsNone(self._account_2.simulate())       

        self.assertEqual(1500 - 10, self._account_1.balance)
        self.assertEqual(round(1500 * 1.01) - 2, self._account_2.balance)
        self.assertEqual(1500, self._account_3.balance)

    def test_simulate_accounts_incentives(self):
        self._bank.add_incentive("Inc1", 10)
        self._bank.add_incentive("Inc2", 20)
        self._bank.add_incentive("Inc3", 30)
        self._bank.add_incentive("Inc4", 40)
        self._bank.add_incentive("Inc5", 50)

        self._bank.assign_incentives(("aa11", "Inc1"), ("aa11", "Inc2"), ("bb22", "Inc3"), ("bb22", "Inc4"), ("cc33", "Inc5"))

        self.assertIsNone(self._account_1.simulate())
        self.assertIsNone(self._account_2.simulate())
        transaction = self._account_3.simulate()

        self.assertEqual(1500 - 10 + 10 + 20, self._account_1.balance)
        self.assertEqual(round(1500 * 1.01) - 2 + 30 + 40, self._account_2.balance)
        self.assertEqual(1500, self._account_3.balance)        

    def test_simulate_escrow(self):
        self._bank.add_incentive("Inc1", 10)
        self._bank.assign_incentives(("cc33", "Inc1"))
       
        self.assertEqual(("cc33", "aa11", round(1500*0.02) + 10), self._account_3.simulate())
        self.assertEqual(2, self._account_3.duration)
        
        self.assertEqual(("cc33", "aa11", round(1500*0.02) + 10), self._account_3.simulate())
        self.assertEqual(1, self._account_3.duration)

        self.assertEqual(("cc33", "aa11", round(1500*0.02) + 10 + 1500), self._account_3.simulate())
        self.assertEqual(0, self._account_3.duration)




