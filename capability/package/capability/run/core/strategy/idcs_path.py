from ontobdc.run.core.port.contex import CliContextPort, CliContextStrategyPort


class IdcsPathStrategy(CliContextStrategyPort):
    def execute(self, context: CliContextPort) -> CliContextPort:
        unprocessed_args = context.unprocessed_args

        if "--idcs-path" in unprocessed_args:
            idx = unprocessed_args.index("--idcs-path")
            if idx + 1 < len(unprocessed_args):
                val = unprocessed_args[idx + 1]
                context.add_parameter(
                    "idcs_path",
                    {
                        "value": val,
                        "uri": "org.local.domain.context.strategy.parameter.idcs_path",
                        "param_uri": "org.local.domain.idcs.input.path",
                    },
                )
                context.clear_parameters(["--idcs-path", val])
            else:
                raise ValueError("Missing value for --idcs-path.")

        return context

