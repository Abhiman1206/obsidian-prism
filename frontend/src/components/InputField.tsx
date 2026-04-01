type InputFieldProps = {
  id: string;
  label: string;
  value: string;
  placeholder: string;
  error?: string;
  onChange: (nextValue: string) => void;
};

export function InputField({
  id,
  label,
  value,
  placeholder,
  error,
  onChange,
}: InputFieldProps) {
  return (
    <label className="field" htmlFor={id}>
      <span className="field__label">{label}</span>
      <input
        id={id}
        name={id}
        className={error ? "field__input field__input--error" : "field__input"}
        value={value}
        placeholder={placeholder}
        onChange={(event) => {
          onChange(event.target.value);
        }}
      />
      {error ? (
        <span role="alert" className="field__error">
          {error}
        </span>
      ) : null}
    </label>
  );
}
