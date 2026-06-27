import {
  AfterViewInit,
  Component,
  ElementRef,
  OnChanges,
  OnDestroy,
  input,
  viewChild,
} from '@angular/core';
import {
  Chart,
  Filler,
  Legend,
  LineElement,
  PointElement,
  RadarController,
  RadialLinearScale,
  Tooltip,
} from 'chart.js';

Chart.register(RadarController, RadialLinearScale, PointElement, LineElement, Filler, Tooltip, Legend);

export interface RadarAxis {
  axis: string;
  score: number;
  target: number;
}

@Component({
  selector: 'app-radar-chart',
  template: '<canvas #canvas></canvas>',
})
export class RadarChart implements AfterViewInit, OnChanges, OnDestroy {
  readonly axes = input<RadarAxis[]>([]);
  private canvas = viewChild<ElementRef<HTMLCanvasElement>>('canvas');
  private chart?: Chart;

  ngAfterViewInit(): void {
    this.render();
  }

  ngOnChanges(): void {
    this.render();
  }

  ngOnDestroy(): void {
    this.chart?.destroy();
  }

  private render(): void {
    const el = this.canvas()?.nativeElement;
    const data = this.axes();
    if (!el || !data.length) return;
    this.chart?.destroy();
    this.chart = new Chart(el, {
      type: 'radar',
      data: {
        labels: data.map((d) => d.axis),
        datasets: [
          {
            label: 'You',
            data: data.map((d) => d.score),
            borderColor: '#00C853',
            backgroundColor: 'rgba(0,230,118,0.18)',
            pointBackgroundColor: '#00C853',
            borderWidth: 2,
          },
          {
            label: 'Target',
            data: data.map((d) => d.target),
            borderColor: '#9ca3af',
            backgroundColor: 'rgba(156,163,175,0.06)',
            borderDash: [5, 4],
            pointBackgroundColor: '#9ca3af',
            borderWidth: 1.5,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            min: 0,
            max: 10,
            ticks: { stepSize: 2, display: false },
            grid: { color: '#eef0f2' },
            angleLines: { color: '#eef0f2' },
            pointLabels: { font: { size: 12, family: 'Inter' }, color: '#374151' },
          },
        },
        plugins: { legend: { position: 'bottom', labels: { font: { family: 'Inter' }, usePointStyle: true } } },
      },
    });
  }
}
