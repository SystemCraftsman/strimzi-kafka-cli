import click


class _ConditionalRequired(click.Option):

    def __init__(self, *args, **kwargs):
        self.options = kwargs.pop("options")
        assert self.options, "'options' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " This argument is %s with %s" % (self._relation, self.options)
        ).strip()
        super().__init__(*args, **kwargs)

    def _check_options_exist(self, opts):
        return any(opts.get(opt) for opt in self.options)

    def handle_parse_result(self, ctx, opts, args):
        self.required = self._resolve_required(self._check_options_exist(opts))
        return super().handle_parse_result(ctx, opts, args)

    def _resolve_required(self, options_exist):
        raise NotImplementedError


class NotRequiredIf(_ConditionalRequired):
    _relation = "mutually exclusive"

    def _resolve_required(self, options_exist):
        return False if options_exist else self.required


class RequiredIf(_ConditionalRequired):
    _relation = "mutually inclusive"

    def _resolve_required(self, options_exist):
        return options_exist


class RequiredIfValue(click.Option):

    def __init__(self, *args, **kwargs):
        self.option_value_pairs = kwargs.pop("option_value_pairs")
        assert self.option_value_pairs, "'option_value_pairs' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " This argument is required when %s"
            % ", ".join(f"{k}={v}" for k, v in self.option_value_pairs.items())
        ).strip()
        super().__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        self.required = any(
            opts.get(option) == value
            for option, value in self.option_value_pairs.items()
        )
        return super().handle_parse_result(ctx, opts, args)
