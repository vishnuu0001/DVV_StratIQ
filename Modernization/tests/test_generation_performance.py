import os
import threading
import time
import unittest
from unittest.mock import patch

from services.modernizer.prompt_pipeline import (
    _pf_expand_generated_source_closure,
    _pf_generate_project_files_llm,
    _pf_generate_source_delta,
    _pf_repair_java_module_boundaries,
)


class GenerationPerformanceTests(unittest.TestCase):
    def test_java_files_run_in_parallel_dependency_waves(self):
        activity_lock = threading.Lock()
        active = 0
        max_active = 0
        completed = []
        service_started_after = []
        output = {}

        def fake_generate(fname, *args):
            nonlocal active, max_active
            record = args[-4]
            with activity_lock:
                active += 1
                max_active = max(max_active, active)
                if "/service/" in fname:
                    service_started_after.append(set(completed))
            time.sleep(0.04)
            record(f"Demo/{fname}", f"// {fname}")
            with activity_lock:
                completed.append(fname)
                active -= 1

        files = [
            "src/main/java/demo/model/Order.java",
            "src/main/java/demo/dto/OrderDto.java",
            "src/main/java/demo/service/OrderService.java",
        ]
        with patch.dict(os.environ, {"MODERNIZATION_JAVA_FILE_WORKERS": "2"}), patch(
            "services.modernizer.prompt_pipeline._pf_generate_and_record_file",
            side_effect=fake_generate,
        ):
            _pf_generate_project_files_llm(
                files, "Demo", {}, "java", "model", "system", "contracts", "namespace",
                "requirements", "manifest", "request", "guide", "stack", "template",
                "assessment", output, lambda path, content: output.__setitem__(path, content),
                lambda *_args: None, lambda *_args: None, "prompt",
            )

        self.assertGreaterEqual(max_active, 2)
        self.assertEqual(1, len(service_started_after))
        self.assertTrue(set(files[:2]).issubset(service_started_after[0]))
        self.assertEqual(3, len(output))

    def test_closure_does_not_expand_unrequested_tests_and_migrations(self):
        module = "Demo/services/orders-service"
        output = {
            f"{module}/src/main/java/com/demo/orders/entity/Order.java": (
                "package com.demo.orders.entity; @Entity public class Order {}"
            ),
            f"{module}/src/main/java/com/demo/orders/OrderApplication.java": (
                "package com.demo.orders; public class OrderApplication {}"
            ),
        }
        added = _pf_expand_generated_source_closure(output, "Demo")
        self.assertEqual([], added)
        self.assertFalse(any("/src/test/" in path for path in output))
        self.assertFalse(any("/db/migration/" in path for path in output))

    def test_boundary_repair_is_single_pass_per_file(self):
        orders = "Demo/services/orders-service"
        users = "Demo/services/users-service"
        path = f"{orders}/src/main/java/com/demo/orders/OrderService.java"
        output = {
            path: (
                "package com.demo.orders; import com.demo.users.User; "
                "public class OrderService { User user; }"
            ),
            f"{users}/src/main/java/com/demo/users/User.java": (
                "package com.demo.users; public class User {}"
            ),
        }
        repaired = set()
        with patch(
            "services.llm.generate",
            return_value="package com.demo.orders; public class OrderService {}",
        ) as generate:
            first = _pf_repair_java_module_boundaries(
                output, "model", "system", lambda *_args: None, repaired,
            )
            second = _pf_repair_java_module_boundaries(
                output, "model", "system", lambda *_args: None, repaired,
            )
        self.assertEqual(1, first)
        self.assertEqual(0, second)
        self.assertEqual(1, generate.call_count)

    def test_boundary_repair_rejects_semantic_non_convergence(self):
        orders = "Demo/services/orders-service"
        users = "Demo/services/users-service"
        path = f"{orders}/src/main/java/com/demo/orders/OrderService.java"
        original = (
            "package com.demo.orders; import com.demo.users.User; "
            "public class OrderService { User user; }"
        )
        output = {
            path: original,
            f"{users}/src/main/java/com/demo/users/User.java": (
                "package com.demo.users; public class User {}"
            ),
        }
        states = set()
        with patch("services.llm.generate", return_value=original):
            self.assertEqual(1, _pf_repair_java_module_boundaries(
                output, "model", "system", lambda *_args: None, states,
            ))
            with self.assertRaisesRegex(RuntimeError, "did not converge"):
                _pf_repair_java_module_boundaries(
                    output, "model", "system", lambda *_args: None, states,
                )

    def test_complete_closure_delta_is_parallel(self):
        output = {f"Demo/src/Type{i}.java": f"contract-{i}" for i in range(4)}
        lock = threading.Lock()
        active = 0
        max_active = 0

        def generate(files, *_args, **_kwargs):
            nonlocal active, max_active
            path = next(iter(files))
            with lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.04)
            files[path] = f"generated::{path}"
            with lock:
                active -= 1

        with patch.dict(os.environ, {
            "MODERNIZATION_CLOSURE_WORKERS": "2",
        }), patch(
            "services.modernizer.domain_generators.dispatch._ollama_generate_all_sources",
            side_effect=generate,
        ):
            _pf_generate_source_delta(
                output, list(output), {"language": "java"}, "Demo", "model", "system",
                lambda *_args: None,
            )
        self.assertGreaterEqual(max_active, 2)
        self.assertTrue(all(value.startswith("generated::") for value in output.values()))


if __name__ == "__main__":
    unittest.main()
