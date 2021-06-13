import click


class NotRequiredIf(click.Argument):
    # TODO: Refactor here

    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop('not_required_if')
        assert self.not_required_if, "'not_required_if' parameter required"
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        control_options_exist = False

        for not_required_if in self.not_required_if:
            control_options_exist = not_required_if in opts
            if control_options_exist is True:
                break

        if control_options_exist:
            self.required = None

        return super(NotRequiredIf, self).handle_parse_result(
            ctx, opts, args)
