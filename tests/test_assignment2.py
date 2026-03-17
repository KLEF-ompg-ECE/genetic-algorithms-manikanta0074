"""
Autograding Tests — Assignment 2: GA Knapsack (2 experiments)
=============================================================
Section A — Code runs correctly         (25 pts)
Section B — Plot files exist            (25 pts)
Section C — README observations filled  (35 pts)
Section D — Code was modified           (15 pts)
                                  TOTAL  100 pts
"""

import subprocess, sys, os, re


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# =============================================================================
# SECTION A — Code runs correctly  (25 pts)
# =============================================================================

class TestCodeRuns:

    def _run(self):
        return subprocess.run(
            [sys.executable, "ga_knapsack.py"],
            cwd=ROOT, capture_output=True, text=True, timeout=120
        )

    def test_runs_without_error(self):
        r = self._run()
        assert r.returncode == 0, \
            f"Program crashed (exit {r.returncode}):\n{r.stderr[:400]}"

    def test_output_shows_value(self):
        r = self._run()
        assert "Value" in r.stdout, \
            "'Value' not found in output — is print_solution() called?"

    def test_output_shows_weight(self):
        r = self._run()
        assert "Weight" in r.stdout, \
            "'Weight' not found in output — is print_solution() called?"

    def test_output_shows_generations(self):
        r = self._run()
        assert "eneration" in r.stdout, \
            "Generation count not printed"

    def test_multiple_experiment_runs(self):
        r = self._run()
        count = r.stdout.count("Final best value")
        assert count >= 2, \
            f"Expected >=2 runs in output (Exp1 + at least one Exp2), found {count}"


# =============================================================================
# SECTION B — Plot files exist  (25 pts)
# =============================================================================

class TestPlotsExist:

    def _plot(self, fname):
        return os.path.join(ROOT, "plots", fname)

    def test_plots_directory_exists(self):
        assert os.path.isdir(os.path.join(ROOT, "plots")), \
            "plots/ directory not found"

    def test_experiment_1_exists(self):
        assert os.path.isfile(self._plot("experiment_1.png")), \
            "plots/experiment_1.png missing"

    def test_experiment_2a_exists(self):
        assert os.path.isfile(self._plot("experiment_2a.png")), \
            "plots/experiment_2a.png missing (mutation_rate=0.01)"

    def test_experiment_2b_exists(self):
        assert os.path.isfile(self._plot("experiment_2b.png")), \
            "plots/experiment_2b.png missing (mutation_rate=0.05)"

    def test_experiment_2c_exists(self):
        assert os.path.isfile(self._plot("experiment_2c.png")), \
            "plots/experiment_2c.png missing (mutation_rate=0.30)"

    def test_all_plots_non_empty(self):
        plots_dir = os.path.join(ROOT, "plots")
        if not os.path.isdir(plots_dir):
            pytest.skip("plots/ directory missing")
        for fname in ["experiment_1.png", "experiment_2a.png",
                      "experiment_2b.png", "experiment_2c.png"]:
            path = os.path.join(plots_dir, fname)
            if os.path.isfile(path):
                assert os.path.getsize(path) > 1000, \
                    f"{fname} appears empty"


# =============================================================================
# SECTION C — README observations filled in  (35 pts)
# =============================================================================

class TestREADME:

    PLACEHOLDERS = ["YOUR ANSWER", "YOUR OBSERVATION", "YOUR REFLECTION", "PASTE"]

    def _load(self):
        path = os.path.join(ROOT, "README.md")
        assert os.path.isfile(path), "README.md not found"
        return open(path).read()

    def _filled(self, text, marker):
        m = re.search(
            rf"{re.escape(marker)}.*?```\n(.*?)```", text, re.DOTALL)
        if not m:
            return False
        content = m.group(1).strip()
        return bool(content) and not any(p in content for p in self.PLACEHOLDERS)

    def test_student_name_filled(self):
        text = self._load()
        line = text.split("Student Name")[1].split("\n")[0]
        assert "___" not in line, "Student name is still blank"

    def test_q1_answered(self):
        assert self._filled(self._load(), "Q1."), \
            "Q1 still placeholder"

    def test_q2_answered(self):
        assert self._filled(self._load(), "Q2."), \
            "Q2 still placeholder"

    def test_q3_answered(self):
        assert self._filled(self._load(), "Q3."), \
            "Q3 still placeholder"

    def test_exp1_packing_list_pasted(self):
        assert self._filled(self._load(), "Copy the printed packing list"), \
            "Experiment 1 packing list not pasted"

    def test_exp1_observation_written(self):
        assert self._filled(self._load(), "Look at `plots/experiment_1.png`"), \
            "Experiment 1 plot observation still blank"

    def test_exp2_results_table_filled(self):
        text = self._load()
        section = text[text.find("Experiment 2"):text.find("## Summary")]
        rows = [l for l in section.split("\n") if l.startswith("| 0.")]
        filled = [r for r in rows
                  if r.count("|") >= 4 and
                  any(c.strip() not in ("", "Yes", "No", " ")
                      for c in r.split("|")[2:5])]
        assert len(filled) >= 2, \
            f"Experiment 2 table: only {len(filled)} rows have data (need >= 2)"

    def test_exp2_observation_written(self):
        assert self._filled(self._load(), "Compare the three plots"), \
            "Experiment 2 observation still blank"

    def test_exp2_best_rate_answered(self):
        assert self._filled(self._load(), "Which mutation_rate gave the best result"), \
            "Experiment 2 best rate question not answered"

    def test_reflection_written(self):
        assert self._filled(self._load(), "most important thing you learned about Genetic"), \
            "Summary reflection still blank"


# =============================================================================
# SECTION D — Code was modified  (15 pts)
# =============================================================================

class TestCodeModified:

    def _load(self):
        return open(os.path.join(ROOT, "ga_knapsack.py")).read()

    def test_exp2_rate_001_present(self):
        assert "0.01" in self._load(), \
            "mutation_rate=0.01 not found in code"

    def test_exp2_rate_030_present(self):
        code = self._load()
        assert "0.30" in code or "0.3," in code, \
            "mutation_rate=0.30 not found in code"

    def test_exp2_three_plot_saves(self):
        count = self._load().count("experiment_2")
        assert count >= 3, \
            f"Expected 3 experiment_2 plot saves, found {count}"
