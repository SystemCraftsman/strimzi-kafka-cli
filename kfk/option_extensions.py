import click


class NotRequiredIf(click.Option):

    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
                          ' This argument is mutually exclusive with %s' %
                          self.not_required_if
                          ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        options_exist = self.name in opts
        control_options_exist = False

        for not_required_if in self.not_required_if:
            control_options_exist = not_required_if in opts
            if control_options_exist is True:
                break

        if control_options_exist:
            if not options_exist:
                self.required = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)


class RequiredIf(click.Option):

    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.required_if = kwargs.pop('required_if')
        assert self.required_if, "'required_if' parameter required"
        kwargs['help'] = (kwargs.get('help', '') +
                          ' This argument is mutually inclusive with %s' %
                          self.required_if
                          ).strip()
        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        options_exist = self.name in opts
        control_options_exist = False

        for required_if in self.required_if:
            control_options_exist = required_if in opts
            if control_options_exist is True:
                break

        if control_options_exist or options_exist:
            self.required = True
        else:
            self.required = None

        return super(RequiredIf, self).handle_parse_result(
            ctx, opts, args)
