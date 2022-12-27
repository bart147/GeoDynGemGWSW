layer = iface.activeLayer()
print (layer)
field1Id = "VAN_NAAR"
isInv1 = False
field2Id = "BERGING_M3"
isInv2 = True
field3Id = "length"
isInv3 = False

order_field = "order"

featureList = list( layer.getFeatures() )
#featureList = sorted(featureList, key=lambda f: f[field1Id], reverse=isInv1)
#featureList = sorted(featureList, key=lambda f: f[field2Id], reverse=isInv2)
#featureList = sorted(featureList, key=lambda f: f[field3Id], reverse=isInv3)
featureList = sorted(featureList, key=lambda f: (f[field1Id],-f[field2Id],f[field3Id]) )

layer.startEditing()

# add order field
layer.dataProvider().addAttributes( [QgsField(order_field, QVariant.Int)] )
attrIdx = layer.dataProvider().fields().indexFromName( order_field )
layer.updateFields() # tell the vector layer to fetch changes from the provider
            
for i, f in enumerate(featureList):
    ##print (f[field1Id])
    layer.changeAttributeValue(f.id(), attrIdx, i+1)

layer.commitChanges()


