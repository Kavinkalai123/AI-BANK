from fastapi import FastAPI,Request
from pydantic import BaseModel
from bank_code import Bank,Customer,DATABASE
import uvicorn

app = FastAPI()

bank = Bank("AI Bank")

# -------------------------------
# Request Models
# -------------------------------
class SignupRequest(BaseModel):
    name: str
    age: int
    password: str
    mpin: str
    initial_deposit: float

class LoginRequest(BaseModel):
    account_number: int
    password: str

class DepositRequest(BaseModel):
    account_number: int
    amount: float

class WithdrawRequest(BaseModel):
    account_number: int
    amount: float

class TransferRequest(BaseModel):
    from_account: int
    to_account: int
    amount: float
    mpin: str

class BeneficiaryRequest(BaseModel):
    owner_account: int
    beneficiary_account: int
    beneficiary_name: str
    nickname: str

# -------------------------------
# API Endpoints
# -------------------------------

@app.post("/signup")
def signup(data: SignupRequest):
    customer = Customer(data.name, data.age)
    acc = bank.open_account(
        customer,
        data.password,
        data.initial_deposit,
        data.mpin
    )
    return {"message": "Account created", "account_number": acc.account_number}

@app.post("/login")
def login(data: LoginRequest):
    acc = bank.login(data.account_number, data.password)
    if not acc:
        return {"error": "Invalid credentials"}

    return {"message": "Login successful", "account_number": acc.account_number}

@app.post("/deposit")
def deposit(data: DepositRequest):
    acc = bank.login(data.account_number, "data.password")  # load account object only

    if not acc:
        return {"error": "Account not found"}

    acc.deposit(data.amount)
    return {"message": "Amount deposited", "balance": acc.balance}

@app.post("/withdraw")
def withdraw(data: WithdrawRequest):
    acc = bank.login(data.account_number, "data.password")

    if not acc:
        return {"error": "Account not found"}

    acc.withdraw(data.amount)
    return {"message": "Amount withdrawn", "balance": acc.balance}

@app.post("/transfer")
def transfer(data: TransferRequest):
    acc = bank.login(data.from_account, "data.password")

    if not acc:
        return {"error": "Account not found"}

    result = acc.money_transfer(data.to_account, data.amount, data.mpin)
    return result

@app.post("/beneficiary")
def beneficiary(data: BeneficiaryRequest):
    acc = bank.login(data.owner_account, "data.password")

    if not acc:
        return {"error": "Account not found"}

    result = acc.add_beneficiaries(
        data.beneficiary_account,
        data.beneficiary_name,
        data.nickname,
    )
    return result

# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     response = await call_next(request)
#     return response
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)

def main():
    print("kalai")
    uvicorn.run(
        app,
        port=8000
        )
if __name__ == "__main__":
    print("erkav")
    main()