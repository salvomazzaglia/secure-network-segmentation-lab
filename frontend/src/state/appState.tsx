import { createContext, useContext, type Dispatch } from 'react';
import type { AppFilters, AppView, Device, LabEvent, LabSnapshot, ViewMode } from '../models';
import { DEFAULT_FILTERS } from '../models';

export interface AppState {
  lab: LabSnapshot | null;
  loading: boolean;
  error: string | null;
  fromMock: boolean;
  selectedDeviceId: string | null;
  viewMode: ViewMode;
  appView: AppView;
  filters: AppFilters;
  events: LabEvent[];
  wsStatus: 'idle' | 'connecting' | 'open' | 'closed' | 'error';
  approvalOpen: boolean;
  reducedMotion: boolean;
  cameraCommand: 'none' | 'fit' | 'reset' | 'focus';
}

export type AppAction =
  | { type: 'SET_LAB'; lab: LabSnapshot; fromMock: boolean; error?: string | null }
  | { type: 'SET_LOADING'; loading: boolean }
  | { type: 'SET_ERROR'; error: string | null }
  | { type: 'SELECT_DEVICE'; deviceId: string | null }
  | { type: 'SET_VIEW_MODE'; viewMode: ViewMode }
  | { type: 'SET_APP_VIEW'; appView: AppView }
  | { type: 'SET_FILTERS'; filters: Partial<AppFilters> }
  | { type: 'RESET_FILTERS' }
  | { type: 'PUSH_EVENT'; event: LabEvent }
  | { type: 'SET_EVENTS'; events: LabEvent[] }
  | { type: 'SET_WS_STATUS'; status: AppState['wsStatus'] }
  | { type: 'SET_APPROVAL_OPEN'; open: boolean }
  | { type: 'SET_REDUCED_MOTION'; value: boolean }
  | { type: 'SET_CAMERA_COMMAND'; command: AppState['cameraCommand'] }
  | { type: 'APPLY_APPROVAL'; deviceId: string; chosenSegment: Device['current_segment'] };

export const initialState: AppState = {
  lab: null,
  loading: true,
  error: null,
  fromMock: false,
  selectedDeviceId: null,
  viewMode: 'TOPOLOGY',
  appView: 'dashboard',
  filters: { ...DEFAULT_FILTERS },
  events: [],
  wsStatus: 'idle',
  approvalOpen: false,
  reducedMotion: false,
  cameraCommand: 'none',
};

export function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LAB':
      return {
        ...state,
        lab: action.lab,
        fromMock: action.fromMock,
        error: action.error ?? null,
        loading: false,
        events: action.lab.events,
      };
    case 'SET_LOADING':
      return { ...state, loading: action.loading };
    case 'SET_ERROR':
      return { ...state, error: action.error, loading: false };
    case 'SELECT_DEVICE':
      return {
        ...state,
        selectedDeviceId: action.deviceId,
        appView: action.deviceId ? 'device' : state.appView,
      };
    case 'SET_VIEW_MODE':
      return { ...state, viewMode: action.viewMode };
    case 'SET_APP_VIEW':
      return { ...state, appView: action.appView };
    case 'SET_FILTERS':
      return { ...state, filters: { ...state.filters, ...action.filters } };
    case 'RESET_FILTERS':
      return { ...state, filters: { ...DEFAULT_FILTERS } };
    case 'PUSH_EVENT':
      return { ...state, events: [action.event, ...state.events].slice(0, 500) };
    case 'SET_EVENTS':
      return { ...state, events: action.events };
    case 'SET_WS_STATUS':
      return { ...state, wsStatus: action.status };
    case 'SET_APPROVAL_OPEN':
      return { ...state, approvalOpen: action.open };
    case 'SET_REDUCED_MOTION':
      return { ...state, reducedMotion: action.value };
    case 'SET_CAMERA_COMMAND':
      return { ...state, cameraCommand: action.command };
    case 'APPLY_APPROVAL': {
      if (!state.lab) return state;
      const devices = state.lab.devices.map((d) =>
        d.device_id === action.deviceId
          ? {
              ...d,
              current_segment: action.chosenSegment,
              awaiting_approval: false,
              approval_required: false,
              quarantined: action.chosenSegment === 'quarantine',
              security_state:
                action.chosenSegment === 'quarantine'
                  ? ('quarantined' as const)
                  : ('approved' as const),
            }
          : d,
      );
      return {
        ...state,
        lab: { ...state.lab, devices },
        approvalOpen: false,
      };
    }
    default:
      return state;
  }
}

export interface AppContextValue {
  state: AppState;
  dispatch: Dispatch<AppAction>;
}

export const AppContext = createContext<AppContextValue | null>(null);

export function useAppState(): AppContextValue {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppState must be used within AppProvider');
  return ctx;
}

export function filterDevices(devices: Device[], filters: AppFilters): Device[] {
  return devices.filter((d) => {
    if (filters.segment !== 'all' && d.current_segment !== filters.segment) return false;
    if (filters.deviceClass !== 'all' && d.device_class !== filters.deviceClass) return false;
    if (filters.connection !== 'all' && d.connection_type !== filters.connection) return false;
    if (filters.online === 'online' && !d.online) return false;
    if (filters.online === 'offline' && d.online) return false;
    if (d.confidence < filters.confidenceMin || d.confidence > filters.confidenceMax) return false;
    if (filters.securityState !== 'all' && d.security_state !== filters.securityState) return false;
    if (filters.apId !== 'all' && d.ap_id !== filters.apId) return false;
    if (
      filters.serviceCategory !== 'all' &&
      !d.services.some((s) => s.category === filters.serviceCategory)
    ) {
      return false;
    }
    return true;
  });
}
