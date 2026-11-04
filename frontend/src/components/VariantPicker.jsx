function VariantPicker({ variants, selectedIndex, onSelect, id }) {
  if (!variants || variants.length === 0) return null

  const useSwatches = Boolean(variants[0].color)
  const selected = variants[selectedIndex]

  if (useSwatches) {
    return (
      <div className="variant-swatches" id={id}>
        <span className="swatch-name">{selected.label}</span>
        <div className="swatch-dots">
          {variants.map((variant, index) => (
            <button
              key={variant.label}
              type="button"
              className={`swatch-dot${index === selectedIndex ? ' selected' : ''}`}
              style={{ backgroundColor: variant.color || '#ccc' }}
              title={variant.label}
              aria-label={variant.label}
              onClick={() => onSelect(index)}
            />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="variant-list" id={id}>
      {variants.map((variant, index) => (
        <button
          key={variant.label}
          type="button"
          className={`variant-pill${index === selectedIndex ? ' selected' : ''}`}
          onClick={() => onSelect(index)}
        >
          {variant.label}
        </button>
      ))}
    </div>
  )
}

export default VariantPicker