-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8 ;
-- -----------------------------------------------------
-- Schema sweetsdreams
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema sweetsdreams
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `sweetsdreams` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `mydb` ;

-- -----------------------------------------------------
-- Table `sweetsdreams`.`tipomedidasmaterialprimas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`tipomedidasmaterialprimas` (
  `id_medida` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  PRIMARY KEY (`id_medida`))
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`usuario` (
  `id_usuario` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `nombreUsuario` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `contrasenia` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `puesto` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `rol` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  PRIMARY KEY (`id_usuario`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`compra`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`compra` (
  `id_compra` INT NOT NULL AUTO_INCREMENT,
  `totalCompra` VARCHAR(100) NOT NULL,
  `fecha_actualiza` DATETIME NOT NULL,
  `usuario_id_usuario` INT NOT NULL,
  PRIMARY KEY (`id_compra`),
  INDEX `fk_compra_usuario1_idx` (`usuario_id_usuario` ASC) VISIBLE,
  CONSTRAINT `fk_compra_usuario1`
    FOREIGN KEY (`usuario_id_usuario`)
    REFERENCES `sweetsdreams`.`usuario` (`id_usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`materiasprimas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`materiasprimas` (
  `id_materiaPrima` INT NOT NULL AUTO_INCREMENT,
  `cantidad` INT NOT NULL,
  `nombre` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `caducidad` DATETIME NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  `tipomedidasmaterialprimas_id_medida` INT NOT NULL,
  PRIMARY KEY (`id_materiaPrima`),
  INDEX `fk_materiasprimas_tipomedidasmaterialprimas1_idx` (`tipomedidasmaterialprimas_id_medida` ASC) VISIBLE,
  CONSTRAINT `fk_materiasprimas_tipomedidasmaterialprimas1`
    FOREIGN KEY (`tipomedidasmaterialprimas_id_medida`)
    REFERENCES `sweetsdreams`.`tipomedidasmaterialprimas` (`id_medida`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`proveedor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`proveedor` (
  `id_proveedor` INT NOT NULL AUTO_INCREMENT,
  `nombreEmpresa` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `direccion` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `contacto` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  PRIMARY KEY (`id_proveedor`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `mydb`.`detalleCompra`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `mydb`.`detalleCompra` (
  `id_detalleCompra` INT NOT NULL,
  `cantidad` VARCHAR(45) NOT NULL,
  `tipomedidasmaterialprimas_id_medida` INT NOT NULL,
  `compra_id_compra` INT NOT NULL,
  `materiasprimas_id_materiaPrima` INT NOT NULL,
  `proveedor_id_proveedor` INT NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  PRIMARY KEY (`id_detalleCompra`),
  INDEX `fk_detalleCompra_tipomedidasmaterialprimas_idx` (`tipomedidasmaterialprimas_id_medida` ASC) VISIBLE,
  INDEX `fk_detalleCompra_compra1_idx` (`compra_id_compra` ASC) VISIBLE,
  INDEX `fk_detalleCompra_materiasprimas1_idx` (`materiasprimas_id_materiaPrima` ASC) VISIBLE,
  INDEX `fk_detalleCompra_proveedor1_idx` (`proveedor_id_proveedor` ASC) VISIBLE,
  CONSTRAINT `fk_detalleCompra_tipomedidasmaterialprimas`
    FOREIGN KEY (`tipomedidasmaterialprimas_id_medida`)
    REFERENCES `sweetsdreams`.`tipomedidasmaterialprimas` (`id_medida`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_detalleCompra_compra1`
    FOREIGN KEY (`compra_id_compra`)
    REFERENCES `sweetsdreams`.`compra` (`id_compra`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_detalleCompra_materiasprimas1`
    FOREIGN KEY (`materiasprimas_id_materiaPrima`)
    REFERENCES `sweetsdreams`.`materiasprimas` (`id_materiaPrima`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_detalleCompra_proveedor1`
    FOREIGN KEY (`proveedor_id_proveedor`)
    REFERENCES `sweetsdreams`.`proveedor` (`id_proveedor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

USE `sweetsdreams` ;

-- -----------------------------------------------------
-- Table `sweetsdreams`.`caja`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`caja` (
  `id_caja` INT NOT NULL AUTO_INCREMENT,
  `dineroTotal` INT NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  PRIMARY KEY (`id_caja`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`cajaretiro`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`cajaretiro` (
  `id_cajaRetiro` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(300) CHARACTER SET 'utf8mb3' NOT NULL,
  `dineroSacado` FLOAT NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  `caja_id_caja` INT NOT NULL,
  `compra_id_compra` INT NOT NULL,
  PRIMARY KEY (`id_cajaRetiro`),
  INDEX `fk_cajaretiro_caja1_idx` (`caja_id_caja` ASC) VISIBLE,
  INDEX `fk_cajaretiro_compra1_idx` (`compra_id_compra` ASC) VISIBLE,
  CONSTRAINT `fk_cajaretiro_caja1`
    FOREIGN KEY (`caja_id_caja`)
    REFERENCES `sweetsdreams`.`caja` (`id_caja`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_cajaretiro_compra1`
    FOREIGN KEY (`compra_id_compra`)
    REFERENCES `sweetsdreams`.`compra` (`id_compra`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`receta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`receta` (
  `id_receta` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `descripcion` VARCHAR(300) CHARACTER SET 'utf8mb3' NOT NULL,
  `totalGalletas` INT NOT NULL,
  `precioTotal` FLOAT NOT NULL,
  `fecha_actualiza` DATETIME NOT NULL,
  PRIMARY KEY (`id_receta`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`detallereceta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`detallereceta` (
  `id_detalleReceta` INT NOT NULL AUTO_INCREMENT,
  `cantidad` INT NOT NULL,
  `receta_id_receta` INT NOT NULL,
  `materiasprimas_id_materiaPrima` INT NOT NULL,
  `tipomedidasmaterialprimas_id_medida` INT NOT NULL,
  PRIMARY KEY (`id_detalleReceta`),
  INDEX `fk_detallereceta_receta1_idx` (`receta_id_receta` ASC) VISIBLE,
  INDEX `fk_detallereceta_materiasprimas1_idx` (`materiasprimas_id_materiaPrima` ASC) VISIBLE,
  INDEX `fk_detallereceta_tipomedidasmaterialprimas1_idx` (`tipomedidasmaterialprimas_id_medida` ASC) VISIBLE,
  CONSTRAINT `fk_detallereceta_materiasprimas1`
    FOREIGN KEY (`materiasprimas_id_materiaPrima`)
    REFERENCES `sweetsdreams`.`materiasprimas` (`id_materiaPrima`),
  CONSTRAINT `fk_detallereceta_receta1`
    FOREIGN KEY (`receta_id_receta`)
    REFERENCES `sweetsdreams`.`receta` (`id_receta`),
  CONSTRAINT `fk_detallereceta_tipomedidasmaterialprimas1`
    FOREIGN KEY (`tipomedidasmaterialprimas_id_medida`)
    REFERENCES `sweetsdreams`.`tipomedidasmaterialprimas` (`id_medida`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`tipoventa`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`tipoventa` (
  `id_tipoVenta` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  PRIMARY KEY (`id_tipoVenta`))
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`venta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`venta` (
  `id_venta` INT NOT NULL AUTO_INCREMENT,
  `total` FLOAT NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  `caja_id_caja` INT NOT NULL,
  `usuario_id_usuario` INT NOT NULL,
  PRIMARY KEY (`id_venta`),
  INDEX `fk_venta_caja1_idx` (`caja_id_caja` ASC) VISIBLE,
  INDEX `fk_venta_usuario1_idx` (`usuario_id_usuario` ASC) VISIBLE,
  CONSTRAINT `fk_venta_caja1`
    FOREIGN KEY (`caja_id_caja`)
    REFERENCES `sweetsdreams`.`caja` (`id_caja`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_venta_usuario1`
    FOREIGN KEY (`usuario_id_usuario`)
    REFERENCES `sweetsdreams`.`usuario` (`id_usuario`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`galleta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`galleta` (
  `id_galleta` INT NOT NULL AUTO_INCREMENT,
  `nombre` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  `cantidad` INT NOT NULL,
  `precio` FLOAT NOT NULL,
  `caducidad` DATETIME NOT NULL,
  `pesajeGramos` FLOAT NOT NULL,
  `precioPieza` FLOAT NOT NULL,
  `precioGramos` FLOAT NOT NULL,
  `precioPaquete1` FLOAT NOT NULL,
  `precioPaquete2` FLOAT NOT NULL,
  `fecha_creacion` DATETIME NOT NULL,
  `receta_id_receta` INT NOT NULL,
  PRIMARY KEY (`id_galleta`),
  INDEX `fk_galleta_receta1_idx` (`receta_id_receta` ASC) VISIBLE,
  CONSTRAINT `fk_galleta_receta1`
    FOREIGN KEY (`receta_id_receta`)
    REFERENCES `sweetsdreams`.`receta` (`id_receta`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`detalleventas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`detalleventas` (
  `id_detalleVentas` INT NOT NULL AUTO_INCREMENT,
  `cantidad` INT NOT NULL,
  `venta_id_venta` INT NOT NULL,
  `tipoventa_id_tipoVenta` INT NOT NULL,
  `galleta_id_galleta` INT NOT NULL,
  PRIMARY KEY (`id_detalleVentas`),
  INDEX `fk_detalleventas_venta_idx` (`venta_id_venta` ASC) VISIBLE,
  INDEX `fk_detalleventas_tipoventa1_idx` (`tipoventa_id_tipoVenta` ASC) VISIBLE,
  INDEX `fk_detalleventas_galleta1_idx` (`galleta_id_galleta` ASC) VISIBLE,
  CONSTRAINT `fk_detalleventas_tipoventa1`
    FOREIGN KEY (`tipoventa_id_tipoVenta`)
    REFERENCES `sweetsdreams`.`tipoventa` (`id_tipoVenta`),
  CONSTRAINT `fk_detalleventas_venta`
    FOREIGN KEY (`venta_id_venta`)
    REFERENCES `sweetsdreams`.`venta` (`id_venta`),
  CONSTRAINT `fk_detalleventas_galleta1`
    FOREIGN KEY (`galleta_id_galleta`)
    REFERENCES `sweetsdreams`.`galleta` (`id_galleta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`tipomerma`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`tipomerma` (
  `id_tipoMerma` INT NOT NULL AUTO_INCREMENT,
  `descripcion` VARCHAR(100) CHARACTER SET 'utf8mb3' NOT NULL,
  PRIMARY KEY (`id_tipoMerma`))
ENGINE = InnoDB
AUTO_INCREMENT = 3
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `sweetsdreams`.`merma`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `sweetsdreams`.`merma` (
  `id_merma` INT NOT NULL AUTO_INCREMENT,
  `fecha_creacion` DATETIME NOT NULL,
  `tipomerma_id_tipoMerma` INT NOT NULL,
  `materiasprimas_id_materiaPrima` INT NOT NULL,
  `galleta_id_galleta` INT NOT NULL,
  PRIMARY KEY (`id_merma`),
  INDEX `fk_merma_tipomerma1_idx` (`tipomerma_id_tipoMerma` ASC) VISIBLE,
  INDEX `fk_merma_materiasprimas1_idx` (`materiasprimas_id_materiaPrima` ASC) VISIBLE,
  INDEX `fk_merma_galleta1_idx` (`galleta_id_galleta` ASC) VISIBLE,
  CONSTRAINT `fk_merma_materiasprimas1`
    FOREIGN KEY (`materiasprimas_id_materiaPrima`)
    REFERENCES `sweetsdreams`.`materiasprimas` (`id_materiaPrima`),
  CONSTRAINT `fk_merma_tipomerma1`
    FOREIGN KEY (`tipomerma_id_tipoMerma`)
    REFERENCES `sweetsdreams`.`tipomerma` (`id_tipoMerma`),
  CONSTRAINT `fk_merma_galleta1`
    FOREIGN KEY (`galleta_id_galleta`)
    REFERENCES `sweetsdreams`.`galleta` (`id_galleta`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
