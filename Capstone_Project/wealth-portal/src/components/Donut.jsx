import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts'

// Donut chart with a big number in the middle and a legend underneath.
// Used on the Dashboard (run status, feedback) and the Portfolio page (allocation, sectors).
//   data:   [{ name, value, color }]
//   format: how to show each value in the legend/tooltip, e.g. v => `${v}%`
function Donut({ data, centerValue, centerLabel, format = v => v }) {
  return (
    <div>
      <div className="donut-wrap">
        <ResponsiveContainer width="100%" height={220}>
          <PieChart>
            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={62}
              outerRadius={90}
              paddingAngle={3}
              startAngle={90}
              endAngle={-270}       // draw clockwise from 12 o'clock
            >
              {data.map(d => <Cell key={d.name} fill={d.color} />)}
            </Pie>
            <Tooltip formatter={v => format(v)} />
          </PieChart>
        </ResponsiveContainer>

        {/* Number shown in the hole of the donut */}
        <div className="donut-center">
          <div className="donut-center-value">{centerValue}</div>
          <div className="donut-center-label">{centerLabel}</div>
        </div>
      </div>

      <ul className="donut-legend">
        {data.map(d => (
          <li key={d.name}>
            <span className="legend-dot" style={{ background: d.color }} />
            {d.name}
            <strong>{format(d.value)}</strong>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default Donut
