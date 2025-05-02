import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RoomAvailabilityWidgetComponent } from './room-availability-widget.component';

describe('RoomAvailabilityWidgetComponent', () => {
  let component: RoomAvailabilityWidgetComponent;
  let fixture: ComponentFixture<RoomAvailabilityWidgetComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RoomAvailabilityWidgetComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RoomAvailabilityWidgetComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
