import { PropertyCard, type Property } from './PropertyCard';

interface PropertyGridProps {
    properties: Property[];
    onSelect: (id: string) => void;
}

export function PropertyGrid({ properties, onSelect }: PropertyGridProps) {
    if (properties.length === 0) {
        return null;
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {properties.map((property, index) => (
                <PropertyCard
                    key={property.id}
                    property={property}
                    index={index}
                    onSelect={onSelect}
                />
            ))}
        </div>
    );
}
