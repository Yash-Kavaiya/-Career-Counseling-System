import { Component, input } from '@angular/core';

/** Prominent, brand-consistent "AI self-prep assistant" disclaimer. */
@Component({
  selector: 'app-disclaimer-banner',
  template: `
    <div class="inline-flex items-center gap-2 rounded-2xl bg-gray-50 border border-gray-100 px-3.5 py-1.5 text-xs text-gray-500">
      <span class="w-2 h-2 rounded-full gb-gradient"></span>
      {{ text() }}
    </div>
  `,
})
export class DisclaimerBanner {
  readonly text = input(
    'AI self-prep assistant — suggestions only, not a substitute for professional career advice.',
  );
}
