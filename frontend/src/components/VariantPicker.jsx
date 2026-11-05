// onPreview(index) is called while the mouse (or keyboard focus) is on a
// variant, and onPreview(null) when it leaves, so the parent can show that
// variant's image without selecting it. previewIndex is the variant being previewed.
function VariantPicker({ variants, selectedIndex, previewIndex, onSelect, onPreview, id }) {
  if (!variants || variants.length === 0) return null

  const useSwatches = Boolean(variants[0].color)
  const shown = variants[previewIndex ?? selectedIndex]

  function previewProps(index) {
    if (!onPreview) return {}
    return {
      onMouseEnter: () => onPreview(index),
      onFocus: () => onPreview(index),
    }
  }

  const leaveProps = onPreview
    ? { onMouseLeave: () => onPreview(null), onBlur: () => onPreview(null) }
    : {}

  if (useSwatches) {
    return (
      <div className="variant-swatches" id={id}>
        <span className="swatch-name">{shown.label}</span>
        <div className="swatch-dots" {...leaveProps}>
          {variants.map((variant, index) => (
            <button
              key={variant.label}
              type="button"
              className={`swatch-dot${index === selectedIndex ? ' selected' : ''}`}
              style={{ backgroundColor: variant.color || '#ccc' }}
              title={variant.label}
              aria-label={variant.label}
              onClick={() => onSelect(index)}
              {...previewProps(index)}
            />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="variant-list" id={id} {...leaveProps}>
      {variants.map((variant, index) => (
        <button
          key={variant.label}
          type="button"
          className={`variant-pill${index === selectedIndex ? ' selected' : ''}`}
          onClick={() => onSelect(index)}
          {...previewProps(index)}
        >
          {variant.label}
        </button>
      ))}
    </div>
  )
}

export default VariantPicker
