import click


class NotRequiredIf(click.Option):
    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.options = kwargs.pop("options")
        assert self.options, "'options' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " This argument is mutually exclusive with %s" % self.options
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        control_options_exist = False

        for options in self.options:
            if opts.get(options):
                control_options_exist = True
                break

        if control_options_exist:
            self.required = None

        return super(NotRequiredIf, self).handle_parse_result(ctx, opts, args)


class RequiredIfValue(click.Option):

    def __init__(self, *args, **kwargs):
        self.option_value_pairs = kwargs.pop("option_value_pairs")
        assert self.option_value_pairs, "'option_value_pairs' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " This argument is required when %s"
            % ", ".join(f"{k}={v}" for k, v in self.option_value_pairs.items())
        ).strip()
        super(RequiredIfValue, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        for option, value in self.option_value_pairs.items():
            if opts.get(option) == value:
                self.required = True
                break
        else:
            self.required = None

        return super(RequiredIfValue, self).handle_parse_result(ctx, opts, args)


class RequiredIf(click.Option):
    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.options = kwargs.pop("options")
        assert self.options, "'options' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " This argument is mutually inclusive with %s" % self.options
        ).strip()
        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        control_options_exist = False

        for options in self.options:
            if opts.get(options):
                control_options_exist = True
                break

        if control_options_exist:
            self.required = True
        else:
            self.required = None

        return super(RequiredIf, self).handle_parse_result(ctx, opts, args)
