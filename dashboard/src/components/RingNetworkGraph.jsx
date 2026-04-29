import React, { useEffect, useRef, useCallback } from 'react';
import * as d3 from 'd3';

const NODE_COLORS = {
  account:   { low: '#00FF88', med: '#FFB800', high: '#FF4444', ring: '#FF0000' },
  device:    '#7C7CFF',
  ip:        '#00D4AA',
  address:   '#FF8C00',
};

export function RingNetworkGraph({ data, onNodeClick, width, height = 580 }) {
  // Width defaults to container — resolved in useEffect via ref
  const resolvedWidth = typeof width === 'number' ? width : 900
  const svgRef = useRef(null);
  const simulationRef = useRef(null);

  const getNodeColor = useCallback((node) => {
    if (node.type === 'account') {
      const score = node.risk_score || 0;
      if (score >= 80) return NODE_COLORS.account.ring;
      if (score >= 60) return NODE_COLORS.account.high;
      if (score >= 30) return NODE_COLORS.account.med;
      return NODE_COLORS.account.low;
    }
    return NODE_COLORS[node.type] || '#888';
  }, []);

  useEffect(() => {
    if (!data || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Background grid
    const defs = svg.append('defs');
    const pattern = defs.append('pattern')
      .attr('id', 'grid').attr('width', 30).attr('height', 30)
      .attr('patternUnits', 'userSpaceOnUse');
    pattern.append('path')
      .attr('d', 'M 30 0 L 0 0 0 30')
      .attr('fill', 'none').attr('stroke', 'rgba(0,212,170,0.05)').attr('stroke-width', 1);
    svg.append('rect').attr('width', resolvedWidth).attr('height', height)
      .attr('fill', 'url(#grid)');

    // Glow filter
    const filter = defs.append('filter').attr('id', 'glow');
    filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur');
    const feMerge = filter.append('feMerge');
    feMerge.append('feMergeNode').attr('in', 'coloredBlur');
    feMerge.append('feMergeNode').attr('in', 'SourceGraphic');

    const g = svg.append('g');

    // Zoom behavior
    const zoom = d3.zoom()
      .scaleExtent([0.3, 4])
      .on('zoom', (event) => g.attr('transform', event.transform));
    svg.call(zoom);

    // Deep clone to avoid D3 mutation issues
    const nodes = data.nodes.map(n => ({ ...n }));
    const links = data.links.map(l => ({ ...l }));

    // Force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links)
        .id(d => d.id)
        .distance(d => d.relationship === 'USES_DEVICE' ? 60 : 100)
        .strength(0.8))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(resolvedWidth / 2, height / 2))
      .force('collision', d3.forceCollide(30));

    simulationRef.current = simulation;

    // Draw links
    const link = g.append('g').selectAll('line')
      .data(links).join('line')
      .attr('stroke', d => {
        const colors = { USES_DEVICE: '#7C7CFF', SHARES_ADDRESS: '#FF4444',
                         SHARES_IP: '#FFB800', SAME_PHONE: '#FF0044' };
        return colors[d.relationship] || '#444';
      })
      .attr('stroke-width', d => d.relationship === 'SHARES_ADDRESS' ? 3 : 1.5)
      .attr('stroke-opacity', 0.7)
      .attr('stroke-dasharray', d => d.relationship === 'SHARES_IP' ? '4,4' : null);

    // Draw nodes
    const node = g.append('g').selectAll('g')
      .data(nodes).join('g')
      .attr('cursor', 'pointer')
      .call(d3.drag()
        .on('start', (event, d) => {
          if (!event.active) simulation.alphaTarget(0.3).restart();
          d.fx = d.x; d.fy = d.y;
        })
        .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
        .on('end', (event, d) => {
          if (!event.active) simulation.alphaTarget(0);
          d.fx = null; d.fy = null;
        }))
      .on('click', (event, d) => onNodeClick?.(d));

    // Node circle
    node.append('circle')
      .attr('r', d => d.type === 'account' ? 14 : 8)
      .attr('fill', getNodeColor)
      .attr('filter', d => (d.risk_score || 0) >= 80 ? 'url(#glow)' : null)
      .attr('stroke', d => d.id === data.account_id ? '#fff' : 'transparent')
      .attr('stroke-width', 2);

    // Pulse animation for high-risk nodes
    node.filter(d => (d.risk_score || 0) >= 80)
      .append('circle')
      .attr('r', 14)
      .attr('fill', 'none')
      .attr('stroke', '#FF4444')
      .attr('stroke-width', 2)
      .attr('opacity', 0.6)
      .append('animate')
        .attr('attributeName', 'r').attr('from', 14).attr('to', 24)
        .attr('dur', '1.5s').attr('repeatCount', 'indefinite');

    // Node labels
    node.append('text')
      .text(d => d.type === 'account' ? d.id.slice(-6) : d.type[0].toUpperCase())
      .attr('dy', d => d.type === 'account' ? 28 : 18)
      .attr('text-anchor', 'middle')
      .attr('fill', '#aaa')
      .attr('font-size', 10)
      .attr('font-family', 'Space Mono, monospace');

    // Tick update
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
      node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    return () => simulation.stop();
  }, [data, resolvedWidth, height, getNodeColor, onNodeClick]);

  return (
    <div style={{ position: 'relative', width: resolvedWidth, height, overflow: 'hidden', borderRadius: 12 }}>
      <svg ref={svgRef} width={resolvedWidth} height={height}
        style={{ background: '#0A0E1A', display: 'block' }} />
    </div>
  );
}
