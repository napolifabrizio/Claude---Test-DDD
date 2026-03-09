import pytest
from decimal import Decimal

from claude_ddd.contexts.shared.domain.value_objects.money import Money
from claude_ddd.contexts.customers.domain.value_objects.email import Email
from claude_ddd.contexts.customers.domain.value_objects.address import Address


class TestMoney:
    def test_creation(self):
        m = Money.of(100)
        assert m.amount == Decimal("100")
        assert m.currency == "BRL"

    def test_negative_amount_raises(self):
        with pytest.raises(ValueError):
            Money.of(-1)

    def test_addition_same_currency(self):
        result = Money.of(10) + Money.of(20)
        assert result.amount == Decimal("30")

    def test_addition_different_currency_raises(self):
        with pytest.raises(ValueError):
            Money.of(10, "BRL") + Money.of(10, "USD")

    def test_subtraction(self):
        result = Money.of(50) - Money.of(20)
        assert result.amount == Decimal("30")

    def test_subtraction_negative_result_raises(self):
        with pytest.raises(ValueError):
            Money.of(10) - Money.of(20)

    def test_multiplication(self):
        result = Money.of(15) * 3
        assert result.amount == Decimal("45")

    def test_immutability(self):
        m = Money.of(100)
        with pytest.raises(Exception):
            m.amount = Decimal("200")

    def test_equality(self):
        assert Money.of(100) == Money.of(100)
        assert Money.of(100) != Money.of(200)


class TestEmail:
    def test_valid_email(self):
        e = Email("user@example.com")
        assert str(e) == "user@example.com"

    def test_invalid_email_raises(self):
        with pytest.raises(ValueError):
            Email("not-an-email")

    def test_invalid_email_no_domain_raises(self):
        with pytest.raises(ValueError):
            Email("user@")

    def test_immutability(self):
        e = Email("a@b.com")
        with pytest.raises(Exception):
            e.value = "c@d.com"


class TestAddress:
    def test_valid_address(self):
        a = Address(street="Rua A", number="1", city="SP", state="SP", zip_code="00000-000")
        assert str(a) == "Rua A, 1 - SP/SP - 00000-000"

    def test_empty_field_raises(self):
        with pytest.raises(ValueError):
            Address(street="", number="1", city="SP", state="SP", zip_code="00000-000")

    def test_immutability(self):
        a = Address(street="Rua A", number="1", city="SP", state="SP", zip_code="00000-000")
        with pytest.raises(Exception):
            a.street = "Rua B"
