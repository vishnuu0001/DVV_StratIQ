import os
import re
import threading
import time
import unittest
from unittest.mock import patch

from services.modernizer.prompt_pipeline import (
    _pf_expand_generated_source_closure,
    _pf_generate_project_files_llm,
    _pf_generate_source_delta,
    _pf_repair_build_round,
    _pf_repair_java_module_boundaries,
)


class GenerationPerformanceTests(unittest.TestCase):
    def test_compiler_repairs_run_concurrently(self):
        output = {
            f"Demo/src/main/java/demo/Type{i}.java": f"class Type{i} {{}}"
            for i in range(4)
        }
        active = 0
        max_active = 0
        lock = threading.Lock()

        def generate(prompt, **_kwargs):
            nonlocal active, max_active
            with lock:
                active += 1
                max_active = max(max_active, active)
            time.sleep(0.04)
            path = re.search(r"FILE PATH: (.+)", prompt).group(1).strip()
            with lock:
                active -= 1
            return output[path] + " // repaired"

        fixable = {path: ["line 1: ';' expected"] for path in output}
        with patch.dict(os.environ, {"MODERNIZATION_REPAIR_WORKERS": "2"}), patch(
            "services.llm.generate", side_effect=generate,
        ):
            failures = _pf_repair_build_round(
                fixable, 1, 2, output, "", "", "model", "system",
                lambda *_args: None, "java",
            )
        self.assertEqual({}, failures)
        self.assertGreaterEqual(max_active, 2)
        self.assertTrue(all("// repaired" in value for value in output.values()))

    def test_java_closure_never_synthesizes_third_party_com_types(self):
        module = "Demo/services/notification-service"
        consumer = f"{module}/src/main/java/com/demo/notification/Notifier.java"
        output = {
            consumer: (
                "package com.demo.notification;\n"
                "import com.fasterxml.jackson.databind.node.ObjectNode;\n"
                "import com.fasterxml.jackson.databind.ObjectMapper;\n"
                "public class Notifier { ObjectNode payload; ObjectMapper mapper; }\n"
            ),
            f"{module}/src/main/java/com/demo/notification/App.java": (
                "package com.demo.notification; public class App {}"
            ),
        }
        added = _pf_expand_generated_source_closure(output, "Demo")
        self.assertFalse(any(path.endswith("ObjectNode.java") for path in added))
        self.assertFalse(any(path.endswith("ObjectMapper.java") for path in added))

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

    def test_same_named_foreign_exceptions_are_localized_not_boundary_repaired(self):
        photoshop = "ModernizedApp/services/photoshop-service"
        mina = "ModernizedApp/services/mina-service"
        notification = "ModernizedApp/services/notification-service"
        service_path = (
            f"{photoshop}/src/main/java/com/mina/photoshop/service/PhotoshopService.java"
        )
        output = {
            service_path: (
                "package com.mina.photoshop.service; "
                "public class PhotoshopService { void find() { "
                "throw new ResourceNotFoundException(\"missing\"); } }"
            ),
            f"{mina}/src/main/java/com/mina/mina/service/ResourceNotFoundException.java": (
                "package com.mina.mina.service; "
                "public class ResourceNotFoundException extends RuntimeException {}"
            ),
            f"{notification}/src/main/java/com/mina/notification/service/ResourceNotFoundException.java": (
                "package com.mina.notification.service; "
                "public class ResourceNotFoundException extends RuntimeException {}"
            ),
        }
        with patch("services.llm.generate") as generate:
            repaired = _pf_repair_java_module_boundaries(
                output, "model", "system", lambda *_args: None, set(),
            )
        self.assertEqual(0, repaired)
        generate.assert_not_called()

        added = _pf_expand_generated_source_closure(output, "ModernizedApp")
        local_exception = (
            f"{photoshop}/src/main/java/com/mina/photoshop/exception/"
            "ResourceNotFoundException.java"
        )
        self.assertIn(local_exception, added)
        self.assertNotIn("com.mina.mina.service.ResourceNotFoundException", output[service_path])
        self.assertNotIn(
            "com.mina.notification.service.ResourceNotFoundException", output[service_path],
        )

    def test_explicit_foreign_exception_import_is_localized_before_boundary_check(self):
        photoshop = "ModernizedApp/services/photoshop-service"
        mina = "ModernizedApp/services/mina-service"
        service_path = f"{photoshop}/src/main/java/com/mina/photoshop/service/PhotoshopService.java"
        local_fqcn = "com.mina.photoshop.exception.ResourceNotFoundException"
        output = {
            service_path: (
                "package com.mina.photoshop.service;\n"
                "import com.mina.mina.service.ResourceNotFoundException;\n"
                "public class PhotoshopService { ResourceNotFoundException error; }"
            ),
            f"{mina}/src/main/java/com/mina/mina/service/ResourceNotFoundException.java": (
                "package com.mina.mina.service; "
                "public class ResourceNotFoundException extends RuntimeException {}"
            ),
        }
        added = _pf_expand_generated_source_closure(output, "ModernizedApp")
        self.assertIn(
            f"{photoshop}/src/main/java/{local_fqcn.replace('.', '/')}.java", added,
        )
        self.assertIn(f"import {local_fqcn};", output[service_path])
        output[
            f"{photoshop}/src/main/java/{local_fqcn.replace('.', '/')}.java"
        ] = (
            f"package {local_fqcn.rsplit('.', 1)[0]}; "
            "public class ResourceNotFoundException extends RuntimeException {}"
        )
        with patch("services.llm.generate") as generate:
            self.assertEqual(0, _pf_repair_java_module_boundaries(
                output, "model", "system", lambda *_args: None, set(),
            ))
        generate.assert_not_called()

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
