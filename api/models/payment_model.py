from flask_restplus import fields, Model

enroll_model = Model("EnrollAccount", {
    'stripeToken': fields.String,
})


verify_model = Model("VerifyAccount", {
    "firstDeposit": fields.Integer,
    "secondDeposit": fields.Integer
})


charge_model = Model("ChargeUser", {
    "amount": fields.Fixed(decimals=2)
})
