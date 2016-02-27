clean:
	@echo "Cleaning up *.pyc files"
	@find . -name "*.pyc" -delete

setup:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt
	@pip install -r requirements_test.txt

pep8:
	@echo "Checking source-code PEP8 compliance"
	@-pep8 tornwamp --ignore=E501 #,E126,E127,E128

pep8_tests:
	@echo "Checking tests code PEP8 compliance"
	@-pep8 tests --ignore=E501 #,E126,E127,E128

lint:
	@echo "Running pylint"
	@# C0103: Invalid name - disabled because it expects any variable outside a class or function to be a constant
	@# C0301: Line too long
	@# E1102: %s is not callable
	@# R0201: Method could be a function
	@# R0902: Too many instance attributes (%s/%s)
	@# R0903: Too few public methods (%s/%s)
	@# R0904: Too many public methods - disabled due to Tornado's classes
	@# R0913: Too many arguments (%s/%s)
	@# W0106: Expression "%s" is assigned to nothing
	@# W0142: Used * or ** magic
	@# W0223: Method %r is abstract in class %r but is not overridden
	@# W0231: __init__ method from base class %r is not called
	@# W0511: (warning notes in code comments; message varies)
	@# W0603: Using the global statement
	@# W0621: Redefining name %r from outer scope (line %s) - due to main if __name__ == '__main__'

	@echo "Running pylint"
	@pylint tornwamp --disable=C0301 --disable=E1102 --disable=R0201 --disable=R0902 --disable=R0903 --disable=R0904 --disable=R0913 --disable=C0103 --disable=W0106 --disable=W0142 --disable=W0223 --disable=W0231 --disable=W0511 --disable=W0603 --disable=W0621

tests: clean pep8 pep8_tests
	@echo "Running pep8, unit and integration tests..."
	@tox
