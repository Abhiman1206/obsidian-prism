import type { PipelineMode } from "../lib/types";

type ModeSelectProps = {
  value: PipelineMode;
  error?: string;
  onChange: (mode: PipelineMode) => void;
};

export function ModeSelect({ value, error, onChange }: ModeSelectProps) {
  return (
    <label className="field" htmlFor="mode">
      <span className="field__label">Execution Mode</span>
      <select
        id="mode"
        name="mode"
        value={value}
        className={error ? "field__input field__input--error" : "field__input"}
        onChange={(event) => {
          onChange(event.target.value as PipelineMode);
        }}
      >
        <option value="crewai">crewai</option>
        <option value="langgraph">langgraph</option>
      </select>
      {error ? (
        <span role="alert" className="field__error">
          {error}
        </span>
      ) : null}
    </label>
  );
}
