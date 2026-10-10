package co.edu.cesde.inventarionoche.application.mapper;

import co.edu.cesde.inventarionoche.application.dto.MovimientoDTO;
import co.edu.cesde.inventarionoche.domain.model.Movimiento;
import org.mapstruct.Mapper;

import java.util.List;

@Mapper(componentModel = "spring", uses = ProductoMapper.class)
public interface MovimientoMapper {

    MovimientoDTO toDto(Movimiento movimiento);

    Movimiento toEntity(MovimientoDTO dto);

    List<MovimientoDTO> toDtoList(List<Movimiento> movimientos);
}
