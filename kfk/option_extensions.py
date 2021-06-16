import click


class NotRequiredIf(click.Option):

    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.options = kwargs.pop('options')
        assert self.options, "'options' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
                          ' This argument is mutually exclusive with %s' %
                          self.options
                          ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        control_options_exist = False

        for options in self.options:
            control_options_exist = options in opts
            if control_options_exist is True:
                break

        if control_options_exist:
            self.required = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)


class RequiredIf(click.Option):

    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.options = kwargs.pop('options')
        assert self.options, "'options' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
                          ' This argument is mutually inclusive with %s' %
                          self.options
                          ).strip()
        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        control_options_exist = False

        for options in self.options:
            control_options_exist = options in opts
            if control_options_exist is True:
                break

        if control_options_exist:
            self.required = True
        else:
            self.required = None

        return super(RequiredIf, self).handle_parse_result(
            ctx, opts, args)
