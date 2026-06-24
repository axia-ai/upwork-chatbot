// Topographic contour motif — the brand's signature mark. Nested irregular
// "elevation" rings, used as a backdrop on the hero, product cards, and chat.

const RING =
  'M200 38 C283 30 352 92 358 158 C363 222 305 272 224 270 C150 268 62 256 50 178 C40 112 117 46 200 38 Z'
const SCALES = [1, 0.84, 0.68, 0.53, 0.39, 0.26, 0.14]

export function Topo({
  className = '',
  strokeWidth = 1,
}: {
  className?: string
  strokeWidth?: number
}) {
  return (
    <svg
      viewBox="0 0 400 300"
      preserveAspectRatio="xMidYMid slice"
      className={className}
      aria-hidden="true"
    >
      {SCALES.map((s, i) => (
        <path
          key={i}
          d={RING}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          transform={`translate(200 154) scale(${s}) translate(-200 -154)`}
        />
      ))}
    </svg>
  )
}

// Compact 8-point star used as the brand mark.
export function NorthStar({ className = '' }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" className={className} aria-hidden="true">
      <path
        d="M12 2.5l1.7 6 4.3-3-3 4.3 6 1.7-6 1.7 3 4.3-4.3-3-1.7 6-1.7-6-4.3 3 3-4.3-6-1.7 6-1.7-3-4.3 4.3 3 1.7-6z"
        fill="currentColor"
      />
    </svg>
  )
}
