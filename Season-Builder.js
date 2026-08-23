const PYODIDE_VERSION = "314.0.4";
const PYODIDE_ROOT = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;
const BASE_SNAPSHOT = "F1-2026-MOD-BN.sna";
const SUPPLIED_SEASONS = new Set(["1985", "1987", "1989", "1991", "1993", "2020"]);
const INPUT_KINDS = ["teams", "drivers", "sponsors", "races", "colours"];

const form = document.querySelector("#builder-form");
const preset = document.querySelector("#season-preset");
const customInputs = document.querySelector("#custom-inputs");
const yearInput = document.querySelector("#year");
const suffixInput = document.querySelector("#suffix");
const buildButton = document.querySelector("#build-button");
const status = document.querySelector("#status");
const statusText = document.querySelector("#status-text");

const fileInputs = {
  teams: document.querySelector("#teams-file"),
  drivers: document.querySelector("#drivers-file"),
  sponsors: document.querySelector("#sponsors-file"),
  races: document.querySelector("#races-file"),
  colours: document.querySelector("#colours-file"),
};

let pyodide;
let baseSnapshot;
let engineReady = false;

function setStatus(message, state = "busy") {
  status.dataset.state = state;
  statusText.textContent = message;
}

function safeSuffix(value) {
  const suffix = value.trim();
  if (!suffix) {
    throw new Error("Please provide an output-name suffix.");
  }
  if (suffix.includes("/") || suffix.includes("\\") || suffix === "." || suffix === "..") {
    throw new Error("The output-name suffix cannot contain a slash.");
  }
  return suffix;
}

function updateSeasonFields() {
  const selected = preset.value;
  customInputs.hidden = selected !== "custom";

  if (SUPPLIED_SEASONS.has(selected)) {
    suffixInput.value = `Season-${selected}`;
  } else if (selected === "base") {
    suffixInput.value = "Custom";
  } else if (!suffixInput.value || /^Season-\d{4}$/.test(suffixInput.value)) {
    suffixInput.value = "Custom";
  }
}

async function fetchRequired(url, kind = "text") {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Could not load ${url} (HTTP ${response.status}).`);
  }
  return kind === "bytes" ? new Uint8Array(await response.arrayBuffer()) : response.text();
}

async function initialiseEngine() {
  try {
    setStatus("Loading the Python engine…");
    const [{ loadPyodide }, tweakSource, snapshot] = await Promise.all([
      import(`${PYODIDE_ROOT}pyodide.mjs`),
      fetchRequired("Tweak-F1.py"),
      fetchRequired(BASE_SNAPSHOT, "bytes"),
    ]);

    pyodide = await loadPyodide({ indexURL: PYODIDE_ROOT });
    baseSnapshot = snapshot;

    pyodide.FS.mkdirTree("/work");
    pyodide.FS.writeFile("/work/Tweak-F1.py", tweakSource, { encoding: "utf8" });
    pyodide.FS.writeFile(`/work/${BASE_SNAPSHOT}`, baseSnapshot);

    await pyodide.runPythonAsync(`
import importlib.util
import sys

spec = importlib.util.spec_from_file_location("tweak_f1", "/work/Tweak-F1.py")
tweak_f1 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = tweak_f1
spec.loader.exec_module(tweak_f1)
    `);

    engineReady = true;
    buildButton.disabled = false;
    setStatus("Ready — choose your options and create the snapshot.", "ready");
  } catch (error) {
    console.error(error);
    setStatus(`The builder could not start: ${error.message}`, "error");
  }
}

async function writeInput(path, source) {
  let contents;
  if (source instanceof File) {
    contents = new Uint8Array(await source.arrayBuffer());
  } else {
    contents = new TextEncoder().encode(await fetchRequired(source));
  }
  pyodide.FS.writeFile(path, contents);
}

async function prepareInputs(selected) {
  const paths = {};

  if (SUPPLIED_SEASONS.has(selected)) {
    for (const kind of INPUT_KINDS) {
      const spelling = kind === "colours" ? "colors" : kind;
      const path = `/work/${kind}.txt`;
      await writeInput(path, `Inputs/${spelling}_${selected}.txt`);
      paths[kind] = path;
    }
    return paths;
  }

  if (selected === "custom") {
    for (const kind of INPUT_KINDS) {
      const file = fileInputs[kind].files[0];
      if (file) {
        const path = `/work/${kind}.txt`;
        await writeInput(path, file);
        paths[kind] = path;
      }
    }
  }

  return paths;
}

function downloadSnapshot(filename, data) {
  const blob = new Blob([data], { type: "application/octet-stream" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function hasCustomSelection(paths, config) {
  return Boolean(
    Object.keys(paths).length
    || config.year
    || config.doubleStartingMoney
    || config.automaticHumanPitStops
    || config.randomIncidents
  );
}

async function buildSnapshot(event) {
  event.preventDefault();
  if (!engineReady) {
    return;
  }

  buildButton.disabled = true;
  setStatus("Preparing the season files…");

  try {
    const selected = preset.value;
    const suffix = safeSuffix(suffixInput.value);
    const paths = await prepareInputs(selected);
    const year = SUPPLIED_SEASONS.has(selected)
      ? Number(selected)
      : (selected === "custom" && yearInput.value ? Number(yearInput.value) : null);

    if (year !== null && (!Number.isInteger(year) || year < 1000 || year > 9999)) {
      throw new Error("The starting year must contain four digits.");
    }

    const config = {
      source: `/work/${BASE_SNAPSHOT}`,
      suffix,
      year,
      paths,
      doubleStartingMoney: document.querySelector("#double-money").checked,
      automaticHumanPitStops: document.querySelector("#automatic-pits").checked,
      randomIncidents: document.querySelector("#incident-rate").value || null,
    };

    if (selected === "base" && !hasCustomSelection(paths, config)) {
      throw new Error("Choose a supplied/custom season or at least one gameplay adjustment.");
    }

    pyodide.globals.set("builder_config_json", JSON.stringify(config));
    setStatus("Patching and verifying the snapshot…");

    const outputPathProxy = await pyodide.runPythonAsync(`
import json
from pathlib import Path

config = json.loads(builder_config_json)
source_path = Path(config["source"])
source = source_path.read_bytes()
if len(source) != tweak_f1.SNA_SIZE:
  raise ValueError(
    f"{source_path.name}: found {len(source)} bytes; "
    f"expected a {tweak_f1.SNA_SIZE}-byte 48K SNA"
  )

paths = config["paths"]
teams = tweak_f1.read_names(Path(paths["teams"]), 6, 8, "team") if "teams" in paths else []
drivers = tweak_f1.read_names(Path(paths["drivers"]), 24, 10, "driver") if "drivers" in paths else []
sponsors = tweak_f1.read_names(Path(paths["sponsors"]), 13, 12, "sponsor") if "sponsors" in paths else []
races = tweak_f1.read_races(Path(paths["races"])) if "races" in paths else []
colours = tweak_f1.read_colours(Path(paths["colours"])) if "colours" in paths else []

variant = tweak_f1.make_variant(
  source,
  teams,
  drivers,
  sponsors,
  colours,
  config["year"],
  races,
  config["doubleStartingMoney"],
  config["automaticHumanPitStops"],
  config["randomIncidents"],
)

suffix = tweak_f1.valid_suffix(config["suffix"])
output_path = Path("/work") / f"{source_path.stem}-{suffix}.sna"
output_path.write_bytes(variant)
str(output_path)
    `);

    const outputPath = outputPathProxy.toString();
    outputPathProxy.destroy?.();
    const output = pyodide.FS.readFile(outputPath);
    const filename = outputPath.split("/").pop();
    downloadSnapshot(filename, output);
    setStatus(`Created ${filename}. Your download should begin now.`, "success");
  } catch (error) {
    console.error(error);
    const lines = (error.message || String(error))
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
    const message = lines.at(-1) || String(error);
    setStatus(`Could not create the snapshot: ${message}`, "error");
  } finally {
    buildButton.disabled = !engineReady;
  }
}

preset.addEventListener("change", updateSeasonFields);
form.addEventListener("submit", buildSnapshot);
updateSeasonFields();
initialiseEngine();
