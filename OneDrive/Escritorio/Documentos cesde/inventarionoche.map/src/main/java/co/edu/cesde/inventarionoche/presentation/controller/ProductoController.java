package co.edu.cesde.inventarionoche.presentation.controller;

import co.edu.cesde.inventarionoche.application.dto.ProductoDTO;
import co.edu.cesde.inventarionoche.application.mapper.ProductoMapper;
import co.edu.cesde.inventarionoche.application.service.ProductoService;
import co.edu.cesde.inventarionoche.domain.model.Producto;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/productos")
@RequiredArgsConstructor
@Tag(name = "Productos", description = "Los productos del inventario")
public class ProductoController {

    private final ProductoService servicioProductos;
    private final ProductoMapper productoMapper;

    @GetMapping
    @Operation(summary = "Ver todos los productos")
    public ResponseEntity<List<ProductoDTO>> findAll() {
        return ResponseEntity.ok(productoMapper.toDtoList(servicioProductos.findAll()));
    }

    @GetMapping("/{id}")
    @Operation(summary = "Buscar un producto por su id")
    public ResponseEntity<ProductoDTO> findById(@PathVariable Long id) {
        return ResponseEntity.ok(productoMapper.toDto(servicioProductos.findById(id)));
    }

    @PostMapping
    @Operation(summary = "Guardar un producto nuevo")
    public ResponseEntity<ProductoDTO> save(@Valid @RequestBody ProductoDTO dto) {
        Producto guardado = servicioProductos.save(productoMapper.toEntity(dto));
        return ResponseEntity.status(HttpStatus.CREATED).body(productoMapper.toDto(guardado));
    }

    @PutMapping
    @Operation(summary = "Cambiar un producto")
    public ResponseEntity<ProductoDTO> update(@Valid @RequestBody ProductoDTO dto) {
        Producto guardado = servicioProductos.update(productoMapper.toEntity(dto));
        return ResponseEntity.ok(productoMapper.toDto(guardado));
    }

    @DeleteMapping("/{id}")
    @Operation(summary = "Borrar un producto")
    public ResponseEntity<Void> delete(@PathVariable Long id) {
        servicioProductos.delete(id);
        return ResponseEntity.noContent().build();
    }
}
