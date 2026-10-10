package co.edu.cesde.inventarionoche.application.mapper;

import co.edu.cesde.inventarionoche.application.dto.ProductoDTO;
import co.edu.cesde.inventarionoche.domain.model.Producto;
import org.mapstruct.Mapper;

import java.util.List;

@Mapper(componentModel = "spring")
public interface ProductoMapper {

    ProductoDTO toDto(Producto producto);

    Producto toEntity(ProductoDTO dto);

    List<ProductoDTO> toDtoList(List<Producto> productos);
}
