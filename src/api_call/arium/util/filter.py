class PortfolioFilter:
    def __init__(self, column, options=None, portfolio_options=None, values=None, industry_codes=None,
                 inverted=False, include_null=False, domain=None):
        self.key = column + '-0'
        self.column = column
        self.options = options if options is not None else []
        self.portfolio_options = portfolio_options if portfolio_options is not None else []
        self.values = values if values is not None else []
        self.include_null = include_null
        self.inverted = inverted
        self.naics = industry_codes if industry_codes is not None else []
        self.domain = self.set_domain(*sorted(domain)) if domain else None

    def add_value(self, value):
        self.values.append(value)
        return self.values

    def add_industry(self, industry):
        self.naics.append(industry)
        return self.naics

    def set_domain(self, minimum, maximum, from_value=None, to_value=None):
        self.domain = {"min": minimum, "from": from_value, "to": to_value, "max": maximum}
        return self.domain

    def get(self):
        if self.column in ["inceptiondate", "expirationdate"]:
            return {
                "column": self.column,
                "key": self.key,
                "domain": self.domain,
                "includeNull": self.include_null,
                "naics": {"values": self.naics}
            }
        return {
            "column": self.column,
            "key": self.key,
            "filter": {"options": self.options, "values": self.values, "portfolioOptions": self.portfolio_options},
            "includeNull": self.include_null,
            "inverted": self.inverted,
            "naics": {"values": self.naics}
        }
