from abc import ABC, abstractmethod
from . import ai

class InvalidResponseError(Exception):
    pass

class Validator(ABC):

    @abstractmethod
    def validate_response(self, resp):
        pass

    @abstractmethod
    def describe_condition(self):
        pass


class AndValidator(Validator):

    def __init__(self, subvalidators):
        self.subvalidators = subvalidators

    def validate_response(self, resp):
        for v in self.subvalidators:
            v.validate_response(resp)

    def describe_condition(self):
        return " & ".join([
            sv.describe_condition() for sv in self.subvalidators
        ])

class OrValidator(Validator):

    def __init__(self, subvalidators):
        self.subvalidators = subvalidators

    def validate_response(self, resp):
        for v in self.subvalidators:
            print("Trying {}".format(v.describe_condition()))
            try:
                v.validate_response(resp)
                return
            except InvalidResponseError:
                pass

        raise InvalidResponseError("None of {}".format(
            self.describe_condition()
        ))

    def describe_condition(self):
        return " | ".join([
            sv.describe_condition() for sv in self.subvalidators
        ])

    
class NotValidator(Validator):

    def __init__(self, subvalidator):
        self.subvalidator = subvalidator

    def validate_response(self, resp):
        try:
            self.subvalidator(resp)
        except InvalidResponseError:
            return

        raise InvalidResponseError("Not {}".format(
            self.subvalidator.describe_condition()
        ))

    def describe_condition(self):
        return "Not {}".format(self.subvalidator.describe_condition())

class StatusCodeValidator(Validator):

    def __init__(self, status_codes):
        self.status_codes = status_codes

    def validate_response(self, resp):
        if resp.status_code not in self.status_codes:
            raise InvalidResponseError("Invalid status code {}".format(
                resp.status_code
            ))

    def describe_condition(self):
        return "Status Code in {}".format(self.status_codes)

class SizeValidator(Validator):

    def __init__(self, min_size, max_size):
        self.min_size = min_size
        self.max_size = max_size

    def validate_response(self, resp):
        size = len(resp.content)
        if size > self.max_size or size < self.min_size:
            raise InvalidResponseError("{}: Invalid size".format(size))

    def describe_condition(self):
        if self.min_size == self.max_size:
            return "Size {}".format(self.min_size)

        return "Size between {} and {}".format(self.min_size, self.max_size)

class AiValidator(Validator):

    def __init__(self):
        pass
    
    def validate_response(self, resp):
        answer = ai.classify_response(resp)
        
        if answer == "error":
            raise InvalidResponseError("Recognized as invalid page")
        
    def describe_condition(self):
        return "AI"
    
def generate_validator(
        match_status_codes,
        filter_status_codes,
        match_sizes,
        filter_sizes,
):
    validators = []

    codes_validator = gen_status_codes_validator(
        match_status_codes,
        filter_status_codes
    )
    if codes_validator:
        validators.append(codes_validator)

    sizes_validator = gen_sizes_validator(match_sizes, filter_sizes)
    if sizes_validator:
        validators.append(sizes_validators)

    if not validators:
        return None
    elif len(validators) == 1:
        return validators[0]
    else:
        return AndValidator(validators)

    return basic_validator
    # return OrValidator([
    #     basic_validator,
    #     AiValidator(),
    # ])


def gen_status_codes_validator(
        match_status_codes,
        filter_status_codes,
):
    if match_status_codes:
        return StatusCodeValidator(match_status_codes)

    if filter_status_codes:
        return NotValidator(StatusCodeValidator(filter_status_codes))

    return None

def gen_sizes_validator(
        match_sizes,
        filter_sizes,
):
    if match_sizes:
        return create_validator_from_sizes_pairs(match_sizes)
    if filter_sizes:
        return NotValidator(create_validator_from_sizes_pairs(filter_sizes))

def create_validator_from_sizes_pairs(sizes_pairs):
    subvalidators = [
        SizeValidator(min_size, max_size)
        for min_size, max_size in sizes_pairs
    ]
    
    if len(subvalidators) == 1:
        return subvalidators[0]
    else:
        return OrValidator(subvalidators)
