class DecisionEngine:

    def evaluate(self, engine_results):

        print()

        print("=" * 60)

        print("AI Decision Engine")

        print("=" * 60)

        for result in engine_results:

            print(result.engine_name)

            print(result.recommendation.value)

            print(result.confidence)

            print(result.reason)

            print("-" * 60)
