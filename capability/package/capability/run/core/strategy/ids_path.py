from ontobdc.run.core.port.contex import CliContextPort, CliContextStrategyPort


class IdsPathStrategy(CliContextStrategyPort):
    def execute(self, context: CliContextPort) -> CliContextPort:
        unprocessed_args = context.unprocessed_args

        if "--ids-path" in unprocessed_args:
            idx = unprocessed_args.index("--ids-path")
            if idx + 1 < len(unprocessed_args):
                val = unprocessed_args[idx + 1]
                context.add_parameter(
                    "ids_path",
                    {
                        "value": val,
                        "uri": "org.local.domain.context.strategy.parameter.ids_path",
                        "param_uri": "org.local.domain.ids.input.path",
                    },
                )
                context.clear_parameters(["--ids-path", val])
            else:
                raise ValueError("Missing value for --ids-path.")

        return context

