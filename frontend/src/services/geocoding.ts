import type { Location } from '@/types';
import { api } from './api';


export interface GeocodeSuggestion {
  id: string;
  place_name: string;
}

interface AutocompleteResponse {
  suggestions: GeocodeSuggestion[];
}

export const geocodingApi = {
  async autocomplete(query: string): Promise<GeocodeSuggestion[]> {
    const response = await api.get<AutocompleteResponse>('/api/v1/geocoding/autocomplete', {
      params: { q: query },
    });
    return response.data.suggestions;
  },

  async resolve(placeId: string): Promise<Location> {
    const response = await api.get<Location>('/api/v1/geocoding/resolve', {
      params: { place_id: placeId },
    });
    return response.data;
  },
};
